import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT
ARQUIVOS = ("score_kredita.json",)
EIXOS = ("risco", "capacidade", "inclusao", "demografia")
AJUSTES = {"i01": -1, "i03": -1, "i08": 1, "i11": -1}
MENSAIS = {"i01", "i03", "i05", "i06", "i08", "i09", "i10", "i11"}
CAMPOS_METODO = ("id", "nome", "eixo", "origin", "unidade", "kind", "params", "rawFormula", "fonte")
UFS = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split())


def digest(value):
    return hashlib.sha256(value).hexdigest()


def csv_rows(data):
    return csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))


def numero(value):
    if value is None or value == "":
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Número inválido: {value}")
    return result


def mesma_nota(a, b):
    return a == b or (a is not None and b is not None
                      and math.isclose(a, b, rel_tol=0, abs_tol=1e-10))


def competencia(value):
    if not re.fullmatch(r"[0-9]{6}", value):
        raise ValueError(f"Competência inválida: {value}")
    return date(int(value[:4]), int(value[4:]), 1)


def limitar(x, inicio, fim):
    return min(fim, max(inicio, x))


def nota(meta, valor):
    tipo, p = meta["kind"], meta["params"]
    if valor is None or tipo == "none":
        return None
    if tipo == "signed":
        return limitar(50 + 50 * valor / p[0], 0, 100)
    if tipo == "informality":
        a, b, c = p
        return (limitar(30 + 20 * (valor - a) / (b - a), 30, 50) if valor <= b
                else limitar(50 + 50 * (valor - b) / (c - b), 50, 100))
    x = limitar(valor, p[0], p[-1])
    if tipo == "centerlog":
        a, b, c = p
        return 50 * math.log(x / a) / math.log(b / a) if x <= b else 50 + 50 * math.log(x / b) / math.log(c / b)
    a, b = p
    if tipo == "log":
        return limitar(100 * math.log(x / a) / math.log(b / a), 0, 100)
    if tipo == "loginverse":
        return limitar(100 * math.log(b / x) / math.log(b / a), 0, 100)
    if tipo in ("linear", "inverse"):
        return 100 * ((x - a) if tipo == "linear" else (b - x)) / (b - a)
    raise ValueError(f"Transformação desconhecida: {tipo}")


def calcular(municipios, pacote, brutos):
    meta = {ind["id"]: ind for ind in pacote["indicadores"]}
    pesos = pacote["configuracao"]["weights"]
    pesos_m = pacote["pesos_M"]
    ativos = [i for i, peso in pesos.items() if peso > 0 or pesos_m.get(i, 0) > 0]
    por_eixo = [[i for i in ativos if meta[i]["eixo"] == eixo and pesos[i] > 0] for eixo in EIXOS]
    resultados, detalhes = {}, {}
    for codigo, municipio in municipios.items():
        valores = {i: brutos[codigo, i] for i in meta}
        originais = {i: nota(meta[i], valor) for i, valor in valores.items()}
        faltantes = [i for i in ativos if originais[i] is None]
        ajustados = valores.copy()
        notas = originais.copy()
        if faltantes:
            resultados[codigo] = [municipio["populacao"], *([None] * 11),
                                  "indicador bruto ausente: " + ", ".join(faltantes)]
            for i in AJUSTES:
                ajustados[i] = notas[i] = None
        else:
            indice = sum(originais[i] * peso for i, peso in pesos_m.items())
            cap = pacote["configuracao"]["cap"]
            phi = limitar(cap * (indice / 50 - 1), -cap, cap) if pacote["configuracao"]["enabled"] else 0
            for i, sinal in AJUSTES.items():
                ajustados[i] = valores[i] * (1 + sinal * phi)
                notas[i] = nota(meta[i], ajustados[i])

            def eixos(valores_nota):
                return [sum(valores_nota[i] * pesos[i] for i in grupo) / sum(pesos[i] for i in grupo)
                        for grupo in por_eixo]

            com = eixos(notas)
            sem = eixos(originais)
            resultados[codigo] = [municipio["populacao"], sum(com) / 4, sum(sem) / 4, *com,
                                  phi, indice, None, None, None, None]
        for i in meta:
            detalhes[codigo, i] = (ajustados[i], notas[i], originais[i])

    ordenados = sorted((c for c, r in resultados.items() if r[1] is not None),
                       key=lambda c: (-resultados[c][1], c))
    for pos, codigo in enumerate(ordenados, 1):
        resultados[codigo][9] = pos
    for campo, coluna in (("uf", 10), ("regiao", 11)):
        por_grupo = sorted(ordenados, key=lambda c: municipios[c][campo])
        for _, grupo in groupby(por_grupo, key=lambda c: municipios[c][campo]):
            for pos, codigo in enumerate(grupo, 1):
                resultados[codigo][coluna] = pos
    return {c: tuple(r) for c, r in resultados.items()}, detalhes


def mes_referencia(ref):
    mensal = re.fullmatch(r"(\d{4})-(0[1-9]|1[0-2])(?: / população\d{4})?", ref)
    if mensal:
        return int(mensal[1]) * 12 + int(mensal[2])
    anual = re.fullmatch(r"(?:\d{4}[–-])?(\d{4})", ref)
    if anual:
        return int(anual[1]) * 12 + 12
    por_data = re.fullmatch(r"\d{2}/(0[1-9]|1[0-2])/(\d{4})(?: / população\d{4})?", ref)
    if por_data:
        data = datetime.strptime(ref.split(" / ")[0], "%d/%m/%Y")
        return data.year * 12 + data.month
    return None


def escolher(candidatos, indicador, mes):
    elegiveis = []
    for obs in candidatos:
        origem = mes_referencia(obs[4])
        if origem is not None and origem < mes and (indicador not in MENSAIS or (
            re.match(r"\d{4}-\d{2}", obs[4]) and mes - origem <= 3
        )):
            elegiveis.append((origem, obs))
    if not elegiveis:
        return None
    recente = max(origem for origem, _ in elegiveis)
    melhores = {obs for origem, obs in elegiveis if origem == recente}
    if len(melhores) != 1:
        raise ValueError(f"Observações conflitantes na referência mais recente de {indicador}.")
    return melhores.pop()


def checar_metodo(pacote):
    _, base, municipios, esperado, obs, detalhes, periodo, _ = ler_exportacao(BASE)

    def definicoes(dados):
        return {ind["id"]: tuple(ind[k] for k in CAMPOS_METODO) for ind in dados["indicadores"]}

    for campo in ("base_version", "configuracao", "pesos_finais", "pesos_M"):
        if pacote[campo] != base[campo]:
            raise ValueError(f"A metodologia do lote mudou em {campo}. Valide o novo cálculo antes de publicar.")
    if definicoes(pacote) != definicoes(base):
        raise ValueError("A definição dos indicadores mudou. Valide o novo método antes de publicar.")
    simulado, auditoria = calcular(municipios, base, {k: obs[v[0]][5] for k, v in detalhes.items()})
    for codigo, valores in esperado.items():
        atual = simulado[codigo]
        if atual[9:] != valores[9:] or any(not mesma_nota(a, b) for a, b in zip(atual[:9], valores[:9])):
            raise ValueError(f"Cálculo local diverge da edição de referência em {codigo}.")
    for chave, valores in auditoria.items():
        if any(not mesma_nota(a, b) for a, b in zip(valores, detalhes[chave][3:6])):
            raise ValueError(f"Cálculo local diverge da auditoria de referência em {chave}.")
    return periodo


def chave_observacao(obs):
    return digest(json.dumps(obs, ensure_ascii=False).encode("utf-8"))


def ler_historicas(conteudo, municipios, indicadores, versao):
    ufs = {m["uf"] for m in municipios.values()}
    for row in csv_rows(conteudo):
        i = row["indicador"]
        meta = indicadores[i]
        municipio, uf = row["municipio"] or None, row["uf"] or None
        val = numero(row["valor_bruto"])
        referencia = row["referencia"]
        valido = (municipio is None and uf in ufs
                  if meta["origin"] == "UF" else municipio in municipios and uf is None)
        if (not valido or row["versao"] != versao or row["unidade"] != meta["unidade"]
                or row["fonte"] != meta["fonte"] or mes_referencia(referencia) is None or val is None
                or (i in MENSAIS and not re.match(r"\d{4}-\d{2}", referencia))):
            raise ValueError(f"Observação histórica inválida: {i}, {municipio or uf}, {referencia}")
        yield (i, municipio, uf, row["fonte"], referencia, val, "observado"), meta["unidade"]


def preparar(conn, dados, pasta):
    hashes, pacote, municipios, ranking, obs, detalhes, periodo, historico = dados
    if periodo <= checar_metodo(pacote):
        raise ValueError("O reaproveitamento vale somente depois da edição de referência.")
    hashes, obs, detalhes = dict(hashes), dict(obs), dict(detalhes)
    indicadores = {ind["id"]: ind for ind in pacote["indicadores"]}
    versao = pacote["base_version"]
    mes = periodo.year * 12 + periodo.month

    caged = (pasta / "caged_i06_zeros.csv").read_bytes()
    hashes["caged_i06_zeros.csv"] = digest(caged)
    estados = {}
    for row in csv_rows(caged):
        codigo, estado = row["codigo_ibge"], row["situacao"]
        if codigo in estados or estado not in ("confirmado", "sem_registro"):
            raise ValueError(f"Situação inválida ou duplicada do zero I06: {codigo}.")
        estados[codigo] = estado
    zeros = {c for c in municipios if obs[detalhes[c, "i06"][0]][5] == 0}
    if estados.keys() != zeros:
        raise ValueError("Classifique todos os zeros de I06, sem acrescentar municípios com outro valor.")

    registro = {}
    arquivo = pasta / "observacoes_historicas.csv"
    if arquivo.exists():
        conteudo = arquivo.read_bytes()
        hashes[arquivo.name] = digest(conteudo)
        for observacao, unidade in ler_historicas(conteudo, municipios, indicadores, versao):
            h = chave_observacao(observacao)
            obs[h] = observacao
            registro[h] = unidade
    candidatos = defaultdict(list)

    for *valores, unidade in conn.execute(
        """SELECT DISTINCT o.indicador,o.municipio,o.uf,o.fonte,o.referencia,o.valor_bruto,o.situacao,si.unidade
           FROM score_indicadores si JOIN observacoes o ON o.id=si.observacao_id
           JOIN edicoes_score e ON e.id=si.edicao_id
           WHERE e.tipo='publicado' AND e.competencia < %s AND e.versao=%s AND o.situacao='observado'
           AND NOT si.reaproveitado
           AND (o.indicador <> 'i06' OR o.valor_bruto <> 0 OR si.zero_i06_confirmado)
           UNION
           SELECT o.indicador,o.municipio,o.uf,o.fonte,o.referencia,o.valor_bruto,o.situacao,h.unidade
           FROM observacoes_historicas h JOIN observacoes o ON o.id=h.observacao_id
           WHERE h.versao=%s AND o.situacao='observado'""", (periodo, versao, versao)
    ):
        candidatos[(*valores[:4], unidade)].append(tuple(valores))
    for h, unidade in registro.items():
        valores = obs[h]
        candidatos[(*valores[:4], unidade)].append(valores)

    usados, reaproveitados = {}, set()
    for chave, valores in detalhes.items():
        codigo, indicador = chave
        h, _, unidade, *_ = valores
        atual = obs[h]
        if atual[5] is None or (indicador == "i06" and estados.get(codigo) == "sem_registro"):
            anterior = escolher(candidatos[(*atual[:4], unidade)], indicador, mes)
            if anterior:
                atual = anterior
                reaproveitados.add(chave)
            elif atual[5] is not None:
                atual = (*atual[:5], None, "ausente")
            h = chave_observacao(atual)
            obs[h] = atual
            detalhes[chave] = (h, *valores[1:])
        usados[chave] = atual[5]

    novos, valores_nota = calcular(municipios, pacote, usados)
    for chave, (h, nome, unidade, _, _, _, peso) in detalhes.items():
        detalhes[chave] = (h, nome, unidade, *valores_nota[chave], peso)
    hashes["calculo-local-v1"] = digest(json.dumps(
        [(c, i, detalhes[c, i][0]) for c, i in sorted(reaproveitados)]
    ).encode())
    substituicoes = {f"{c}/{i}": obs[detalhes[c, i][0]][4] for c, i in sorted(reaproveitados)}
    previa = {
        "competencia": str(periodo), "observacoes_reaproveitadas": substituicoes,
        "alteracoes": [{"codigo_ibge": c, "score_exportado": r[1], "score_local": novos[c][1],
                        "posicao_exportada": r[9], "posicao_local": novos[c][9],
                        "motivo_sem_score": novos[c][12]}
                       for c, r in ranking.items() if not mesma_nota(r[1], novos[c][1]) or r[9:] != novos[c][9:]],
    }
    confirmado = {c for c, estado in estados.items() if estado == "confirmado"}
    return (hashes, pacote, municipios, novos, obs, detalhes, periodo, historico), (
        reaproveitados, confirmado, registro
    ), previa


def preparar_banco(conn):
    migrations = ROOT / "migrations"
    with conn.transaction(), conn.cursor() as cur:
        for migration in sorted(migrations.glob("*.sql")):
            cur.execute(migration.read_text(encoding="utf-8"))


def importar_apostas(conn, data=None):
    if data is None:
        for caminho in (
            ROOT / "kredita-demo/apostas.json",
            ROOT.parent / "frontend/apostas.json",
            ROOT.parent / "frontend/kredita-demo/apostas.json",
        ):
            if caminho.exists():
                data = json.loads(caminho.read_text(encoding="utf-8"))
                break
    if data is None:
        raise FileNotFoundError("apostas.json não encontrado.")
    rows = data["territorios"]
    if len(rows) != 28 or {row["uf"] for row in rows} != UFS | {"BR"}:
        raise ValueError("A tabela precisa conter Brasil e as 27 UFs, sem duplicatas.")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute((ROOT / "migrations/001_postgresql.sql").read_text(encoding="utf-8"))
        cur.execute(
            """INSERT INTO estudos_apostas (id, estudo, inicio, fim, metrica, unidade, fonte)
               VALUES (%(id)s, %(estudo)s, %(inicio)s, %(fim)s, %(metrica)s, %(unidade)s, %(fonte)s)
               ON CONFLICT (id) DO UPDATE SET estudo=excluded.estudo, inicio=excluded.inicio,
                   fim=excluded.fim, metrica=excluded.metrica, unidade=excluded.unidade, fonte=excluded.fonte""",
            data,
        )
        cur.executemany(
            """INSERT INTO estimativas_apostas (estudo_id, uf, valor, margem_pp, populacao_estimada)
               VALUES (%s,%s,%s,%s,%s) ON CONFLICT (estudo_id, uf) DO UPDATE SET
               valor=excluded.valor, margem_pp=excluded.margem_pp, populacao_estimada=excluded.populacao_estimada""",
            ((data["id"], r["uf"], r["valor"], r["margem_pp"], r["populacao_estimada"]) for r in rows),
        )


def ler_exportacao(pasta):
    files = {name: (pasta / name).read_bytes() for name in ARQUIVOS}
    hashes = {name: digest(data) for name, data in files.items()}
    pacote = json.loads(files["score_kredita.json"].decode("utf-8-sig"))
    config = pacote["configuracao"]
    if (pacote["schema_version"] != "kredita-integracao-2"
            or len(config["axes"]) != len(EIXOS) or set(config["axes"]) != set(EIXOS)):
        raise ValueError("Esperada uma exportação com os quatro eixos do Colab.")
    indicadores = {item["id"]: item for item in pacote["indicadores"]}
    if set(indicadores) != {f"i{i:02}" for i in range(1, 17)} or (
        indicadores["i15"]["kind"] != "none" or config["weights"]["i15"] != 0
    ):
        raise ValueError("Esquema de indicadores incompatível com a exportação canônica.")

    municipios = {}
    for item in pacote["municipios"]:
        codigo = item["cod_municipio"]
        if not re.fullmatch(r"[0-9]{7}", codigo) or codigo in municipios:
            raise ValueError(f"Código municipal inválido ou duplicado: {codigo}")
        if item["score_disponivel"] != (item["score_kredita"] is not None):
            raise ValueError(f"Disponibilidade incoerente: {codigo}")
        municipios[codigo] = item
    periodos = {competencia(item["periodo_referencia"]) for item in municipios.values()}
    if len(periodos) != 1:
        raise ValueError("A exportação deve ter uma competência principal.")

    observacoes = {}
    detalhes = {}
    brutos = {}
    for codigo, item in municipios.items():
        for indicador, meta in indicadores.items():
            chave = (codigo, indicador)
            valor = numero(item["brutos"].get(indicador))
            peso = numero(pacote["pesos_finais"].get(indicador, 0))
            estadual = meta["origin"] == "UF"
            situacao = "observado"
            if valor is None:
                situacao = "ausente"
            elif indicador in item.get("indicadores_estimados", []):
                situacao = "estimado"
            fonte, referencia = meta["fonte"].strip(), meta["periodo"].strip()
            if not fonte or not referencia:
                raise ValueError(f"Observação sem fonte ou referência: {chave}")
            obs = (indicador, None if estadual else codigo, item["uf"] if estadual else None,
                   fonte, referencia, valor, situacao)
            hash_obs = chave_observacao(obs)
            observacoes[hash_obs] = obs
            detalhes[chave] = (hash_obs, meta["nome"], meta["unidade"], None, None, None, peso)
            brutos[chave] = valor

    calculados, auditoria = calcular(municipios, pacote, brutos)
    ranking = {}
    campos = ("score_kredita", "score_sem_cofator", "E1", "E2", "E3", "E4")
    for codigo, item in municipios.items():
        calc = calculados[codigo]
        esperado = (numero(item["populacao"]), *(numero(item[k]) for k in campos),
                    numero(item["phi"]), numero(item["M"]))
        if (calc[9] != item["pos_brasil"]
                or any((p is None) == item["score_disponivel"] for p in calc[9:12])
                or any(not mesma_nota(a, b) for a, b in zip(calc[:9], esperado))):
            raise ValueError(f"Ranking incompatível com o cálculo no JSON: {codigo}")
        ranking[codigo] = (*esperado, *calc[9:12], item.get("motivo_sem_score"))

    for chave, (h, nome, unidade, _, _, _, peso) in list(detalhes.items()):
        detalhes[chave] = (h, nome, unidade, *auditoria[chave], peso)

    historico = {}
    if "historico_scr" in pacote:
        for per_str, m_map in pacote["historico_scr"].items():
            grupo = historico.setdefault(competencia(per_str), {})
            for codigo, vals in m_map.items():
                grupo[codigo] = (numero(municipios[codigo]["populacao"]), *(numero(v) for v in vals))
    elif (pasta / "historico_parcial.csv").exists():
        raw_hist = (pasta / "historico_parcial.csv").read_bytes()
        hashes["historico_parcial.csv"] = digest(raw_hist)
        for row in csv_rows(raw_hist):
            codigo = row["codigo_ibge"]
            item = municipios[codigo]
            grupo = historico.setdefault(competencia(row["periodo"]), {})
            if codigo in grupo:
                raise ValueError(f"Município duplicado na simulação: {codigo}")
            grupo[codigo] = (numero(item["populacao"]), numero(row["score"]),
                             *(numero(row[eixo]) for eixo in EIXOS))
    if not historico or any(grupo.keys() != municipios.keys() for grupo in historico.values()):
        raise ValueError("Simulação incompleta. Meses podem faltar, mas uma competência deve incluir todos os municípios.")
    return hashes, pacote, municipios, ranking, observacoes, detalhes, periodos.pop(), historico


def buscar_json_api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "KREDITA/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def buscar_bytes_api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "KREDITA/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()


def coletar_fontes_publicas(mes_alvo, municipios, fetcher_json=buscar_json_api, fetcher_bytes=buscar_bytes_api):
    ano_mes = mes_alvo.replace("-", "")
    ano = mes_alvo[:4]
    coletados = {"referencias": {}, "fontes_ativas": []}

    # 1. IBGE SIDRA 6579 (População estimada I15 e Variação populacional I13)
    try:
        sidra = fetcher_json("https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last%202")
        por_mun = defaultdict(dict)
        for row in sidra[1:]:
            cod, ano_ref, val = str(row.get("D1C", "")), str(row.get("D3C", "")), row.get("V")
            if re.fullmatch(r"\d{7}", cod) and re.fullmatch(r"\d{4}", ano_ref) and val not in (None, "...", "-", ""):
                por_mun[cod][int(ano_ref)] = float(val)
        anos_disp = sorted({a for m in por_mun.values() for a in m})
        if len(anos_disp) >= 2:
            a_ant, a_atual = anos_disp[-2], anos_disp[-1]
            pop_atual = {c: m[a_atual] for c, m in por_mun.items() if a_atual in m}
            var_pop = {
                c: 100.0 * (m[a_atual] - m[a_ant]) / m[a_ant]
                for c, m in por_mun.items() if a_atual in m and a_ant in m and m[a_ant] > 0
            }
            if pop_atual:
                coletados["i15"] = pop_atual
                coletados["referencias"]["i15"] = str(a_atual)
                coletados["ano_populacao"] = str(a_atual)
                coletados["fontes_ativas"].append("IBGE SIDRA 6579")
            if var_pop:
                coletados["i13"] = var_pop
                coletados["referencias"]["i13"] = f"{a_ant}–{a_atual}"
    except Exception:
        pass

    ano_pop = coletados.get("ano_populacao", "2025")
    pop_mun = {
        c: coletados.get("i15", {}).get(c, numero(m["populacao"]))
        for c, m in municipios.items()
    }
    pop_uf = defaultdict(float)
    for c, m in municipios.items():
        if pop_mun.get(c):
            pop_uf[m["uf"]] += pop_mun[c]

    # 2. BCB Olinda Pix (I09 - Volume Pix PF per capita)
    try:
        url_pix = (
            "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
            f"TransacoesPixPorMunicipio(DataBase=@DataBase)?@DataBase='{ano_mes}'"
            "&$format=json&$select=Municipio_Ibge,VL_PagadorPF"
        )
        pix_rows = fetcher_json(url_pix).get("value", [])
        i09 = {}
        for r in pix_rows:
            cod = str(r.get("Municipio_Ibge") or "").zfill(7)
            val = r.get("VL_PagadorPF")
            if cod in pop_mun and pop_mun[cod] and val is not None:
                i09[cod] = float(val) / pop_mun[cod]
        if i09:
            coletados["i09"] = i09
            coletados["referencias"]["i09"] = f"{mes_alvo} / população{ano_pop}"
            coletados["fontes_ativas"].append("BCB Olinda Pix")
    except Exception:
        pass

    # 3. BCB Olinda Agências Supervisionadas (I16 - Agências por 100 mil hab.)
    try:
        url_ag = (
            "https://olinda.bcb.gov.br/olinda/servico/Informes_Agencias/versao/v1/odata/"
            "Agencias?$format=json&$select=CodigoIbge"
        )
        ag_rows = fetcher_json(url_ag).get("value", [])
        if ag_rows:
            contagem = Counter(str(r.get("CodigoIbge") or "").zfill(7) for r in ag_rows if r.get("CodigoIbge"))
            hoje = date.today().strftime("%d/%m/%Y")
            coletados["i16"] = {
                c: 100000.0 * contagem.get(c, 0) / pop_mun[c]
                for c in municipios if pop_mun.get(c)
            }
            coletados["referencias"]["i16"] = f"{hoje} / população{ano_pop}"
            coletados["fontes_ativas"].append("BCB Informes Agências")
    except Exception:
        pass

    # 4. MDS Dados Abertos / CadÚnico (I10 - Pessoas no CadÚnico por 100 hab.)
    try:
        url_cad = (
            "https://aplicacoes.cidadania.gov.br/vis/data3/v.php?q[]=oNOclsLerpibuKep&"
            f"ag=m&mes={ano_mes}&wt=json"
        )
        cad_data = fetcher_json(url_cad)
        docs = cad_data.get("response", {}).get("docs", cad_data.get("value", []))
        i10 = {}
        for r in docs:
            cod = str(r.get("ibge") or r.get("codigo_ibge") or "").zfill(7)
            qtd = r.get("qtd_pessoas_cadunico") or r.get("pessoas")
            if len(cod) == 6:
                cod = next((c for c in municipios if c.startswith(cod)), cod)
            if cod in pop_mun and pop_mun[cod] and qtd is not None:
                i10[cod] = 100.0 * float(qtd) / pop_mun[cod]
        if i10:
            coletados["i10"] = i10
            coletados["referencias"]["i10"] = f"{mes_alvo} / população{ano_pop}"
            coletados["fontes_ativas"].append("MDS MI Social")
    except Exception:
        pass

    # 5. BCB SCR.data (I01, I03, I11 por UF)
    try:
        raw_scr = fetcher_bytes(f"https://www.bcb.gov.br/pda/desig/planilha_{ano}.zip")
        soma_ativa, soma_inad, soma_v15_90, soma_v90 = defaultdict(float), defaultdict(float), defaultdict(float), defaultdict(float)
        with zipfile.ZipFile(io.BytesIO(raw_scr)) as zf:
            alvo_csv = next((n for n in zf.namelist() if ano_mes in n and n.endswith(".csv")), None)
            if alvo_csv:
                with zf.open(alvo_csv) as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"), delimiter=";")
                    for row in reader:
                        if row.get("cliente") != "PF" or row.get("uf") not in UFS:
                            continue
                        uf = row["uf"]
                        num_pt = lambda k: float((row.get(k) or "0").replace(".", "").replace(",", "."))
                        soma_ativa[uf] += num_pt("carteira_ativa")
                        soma_inad[uf] += num_pt("carteira_inadimplida_arrastada")
                        v15 = sum(num_pt(f"vencido_acima_de_{d}_ate_{fim}_dias") for d, fim in ((15, 30), (31, 60), (61, 90)))
                        v90 = sum(num_pt(k) for k in row if k.startswith("vencido_acima_de_") and k not in (
                            "vencido_acima_de_15_ate_30_dias", "vencido_acima_de_31_ate_60_dias", "vencido_acima_de_61_ate_90_dias"
                        ))
                        soma_v15_90[uf] += v15
                        soma_v90[uf] += v90
        if len(soma_ativa) == 27:
            coletados["i01"] = {uf: 100.0 * soma_inad[uf] / soma_ativa[uf] for uf in UFS if soma_ativa[uf] > 0}
            coletados["i03"] = {
                uf: 100.0 * soma_v90[uf] / (soma_v15_90[uf] + soma_v90[uf])
                for uf in UFS if (soma_v15_90[uf] + soma_v90[uf]) > 0
            }
            coletados["i11"] = {uf: soma_ativa[uf] / pop_uf[uf] for uf in UFS if pop_uf[uf] > 0}
            coletados["referencias"]["i01"] = mes_alvo
            coletados["referencias"]["i03"] = mes_alvo
            coletados["referencias"]["i11"] = f"{mes_alvo} / população{ano_pop}"
            coletados["fontes_ativas"].append("BCB SCR.data")
    except Exception:
        pass

    # 6. BCB ESTBAN (I08 - Crédito / Depósitos por UF)
    try:
        raw_est = fetcher_bytes(f"https://www4.bcb.gov.br/fis/cosif/cont/estban/municipio/{ano_mes}_ESTBAN.ZIP")
        cred_uf, dep_uf = defaultdict(float), defaultdict(float)
        with zipfile.ZipFile(io.BytesIO(raw_est)) as zf:
            csv_name = next((n for n in zf.namelist() if n.lower().endswith(".csv")), None)
            if csv_name:
                with zf.open(csv_name) as f:
                    linhas = (line.decode("latin-1") for line in f if not line.startswith(b"#"))
                    reader = csv.DictReader(linhas, delimiter=";")
                    for row in reader:
                        uf = (row.get("UF") or "").strip()
                        if uf not in UFS:
                            continue
                        num_v = lambda k: float((row.get(k) or "0").replace(",", "."))
                        cred_uf[uf] += num_v("VERBETE_160_OPERACOES_DE_CREDITO")
                        dep_uf[uf] += (
                            num_v("VERBETE_401_DEPOSITOS_A_VISTA_DO_PUBLICO")
                            + num_v("VERBETE_420_DEPOSITOS_DE_POUPANCA")
                            + num_v("VERBETE_432_DEPOSITOS_A_PRAZO")
                        )
        if len(cred_uf) == 27 and all(dep_uf[u] > 0 for u in UFS):
            coletados["i08"] = {uf: cred_uf[uf] / dep_uf[uf] for uf in UFS}
            coletados["referencias"]["i08"] = mes_alvo
            coletados["fontes_ativas"].append("BCB ESTBAN")
    except Exception:
        pass

    return coletados


def atualizar_via_apis(dados, mes_alvo, fetcher=buscar_json_api, fetcher_bytes=buscar_bytes_api):
    hashes, pacote, municipios, _, observacoes, detalhes, _, historico = dados
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", mes_alvo):
        raise ValueError("Use --competencia no formato AAAA-MM.")
    periodo = competencia(mes_alvo.replace("-", ""))
    coletados = coletar_fontes_publicas(mes_alvo, municipios, fetcher_json=fetcher, fetcher_bytes=fetcher_bytes)
    if not coletados["fontes_ativas"]:
        raise ValueError(f"Nenhuma API pública retornou dados novos para {mes_alvo}.")

    pacote = json.loads(json.dumps(pacote))
    municipios = json.loads(json.dumps(municipios))
    observacoes = dict(observacoes)
    detalhes = dict(detalhes)
    hashes = dict(hashes)
    historico = dict(historico)

    if "i15" in coletados:
        for cod, pop_nova in coletados["i15"].items():
            if cod in municipios:
                municipios[cod]["populacao"] = pop_nova

    indicadores = {ind["id"]: ind for ind in pacote["indicadores"]}
    usados = {}
    reaproveitados = set()
    atualizados = 0

    for (codigo, ind), (h, nome, unidade, *_) in list(detalhes.items()):
        obs = observacoes[h]
        valor = obs[5]
        meta = indicadores[ind]
        estadual = meta["origin"] == "UF"
        chave_busca = municipios[codigo]["uf"] if estadual else codigo
        mapa_novo = coletados.get(ind)
        if mapa_novo and chave_busca in mapa_novo:
            valor = mapa_novo[chave_busca]
            ref_nova = coletados["referencias"][ind]
            nova_obs = (ind, None if estadual else codigo, municipios[codigo]["uf"] if estadual else None,
                        meta["fonte"].strip(), ref_nova, valor, "observado")
            h = chave_observacao(nova_obs)
            observacoes[h] = nova_obs
            atualizados += 1
        elif ind in MENSAIS and not obs[4].startswith(mes_alvo):
            reaproveitados.add((codigo, ind))
        detalhes[codigo, ind] = (h, nome, unidade, *detalhes[codigo, ind][3:])
        usados[codigo, ind] = valor

    novos, auditoria = calcular(municipios, pacote, usados)
    for chave, (h, nome, unidade, _, _, _, peso) in list(detalhes.items()):
        detalhes[chave] = (h, nome, unidade, *auditoria[chave], peso)

    if all(k in coletados for k in ("i01", "i03", "i11")) or periodo not in historico:
        historico[periodo] = {
            c: (novos[c][0], novos[c][1], *novos[c][3:7]) for c in municipios
        }

    hashes["atualizacao-api"] = digest(
        json.dumps([mes_alvo, sorted(coletados["fontes_ativas"]), atualizados]).encode("utf-8")
    )
    proveniencia = (reaproveitados, set(), {})
    return (hashes, pacote, municipios, novos, observacoes, detalhes, periodo, historico), atualizados, proveniencia


def publicar(conn, dados, calculado_em=None, proveniencia=None):
    from psycopg.types.json import Jsonb

    hashes, pacote, municipios, ranking, observacoes, detalhes, periodo, historico = dados
    hash_lote = digest(json.dumps(hashes, sort_keys=True).encode("utf-8"))
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "INSERT INTO lotes_importacao(hash, arquivos) VALUES (%s,%s) "
            "ON CONFLICT (hash) DO NOTHING RETURNING id", (hash_lote, Jsonb(hashes)),
        )
        lote = cur.fetchone()
        if lote is None:
            return None
        lote_id = lote[0]
        cur.executemany(
            "INSERT INTO municipios VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
            ((k, m["municipio"], m["uf"], m["regiao"]) for k, m in sorted(municipios.items())),
        )
        cur.executemany(
            "INSERT INTO indicadores VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            ((d["id"], d["nome"], d["unidade"]) for d in sorted(
                pacote["indicadores"], key=lambda d: d["id"])),
        )
        cur.executemany(
            """INSERT INTO observacoes
               (indicador, municipio, uf, fonte, referencia, valor_bruto, situacao, lote_id, hash)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (hash) DO NOTHING""",
            ((*obs, lote_id, h) for h, obs in sorted(observacoes.items())),
        )
        cur.execute("SELECT hash, id FROM observacoes WHERE hash = ANY(%s)", (list(observacoes),))
        ids = dict(cur.fetchall())

        def criar_edicao(mes, tipo):
            cur.execute(
                """INSERT INTO edicoes_score
                   (lote_id, competencia, calculado_em, versao, configuracao, tipo)
                   VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                (lote_id, mes, calculado_em, pacote["base_version"],
                 Jsonb(pacote["configuracao"]), tipo),
            )
            return cur.fetchone()[0]

        edicao = criar_edicao(periodo, "publicado")
        cur.executemany(
            """INSERT INTO scores_municipais
               (edicao_id, codigo_ibge, populacao, score, score_sem_cofator, e1, e2, e3, e4,
                cofator, m, pos_brasil, pos_uf, pos_regiao, motivo_sem_score)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            ((edicao, codigo, *valores) for codigo, valores in ranking.items()),
        )
        cur.executemany(
            """INSERT INTO score_indicadores
               (edicao_id, codigo_ibge, indicador, observacao_id, nome, unidade,
                valor_usado, nota, nota_sem_cofator, peso)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            ((edicao, codigo, indicador, ids[h], *valores)
             for (codigo, indicador), (h, *valores) in detalhes.items()),
        )
        if proveniencia is not None:
            reaproveitados, confirmados, registro = proveniencia
            cur.executemany(
                """UPDATE score_indicadores SET reaproveitado=true
                   WHERE edicao_id=%s AND codigo_ibge=%s AND indicador=%s""",
                ((edicao, codigo, indicador) for codigo, indicador in sorted(reaproveitados)),
            )
            cur.execute(
                """UPDATE score_indicadores SET zero_i06_confirmado=true
                   WHERE edicao_id=%s AND indicador='i06' AND codigo_ibge=ANY(%s)""",
                (edicao, sorted(confirmados)),
            )
            cur.executemany(
                "INSERT INTO observacoes_historicas VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                ((ids[h], pacote["base_version"], unidade) for h, unidade in registro.items()),
            )
        for mes, grupo in sorted(historico.items()):
            simulacao = criar_edicao(mes, "simulacao_scr")
            cur.executemany(
                """INSERT INTO scores_municipais
                   (edicao_id, codigo_ibge, populacao, score, e1, e2, e3, e4)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                ((simulacao, codigo, *valores) for codigo, valores in grupo.items()),
            )
    return edicao


def main():
    parser = argparse.ArgumentParser(description="Gerencia migrações, importação, cálculo e atualização do KREDITA.")
    parser.add_argument("pasta", nargs="?", default=ROOT, type=Path, help="Pasta com score_kredita.json")
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--validar", action="store_true", help="Valida os arquivos sem publicar")
    modo.add_argument("--prever-recalculo", action="store_true", help="Gera a prévia local sem publicar")
    modo.add_argument("--publicar-recalculado", action="store_true", help="Recalcula e publica uma nova edição")
    modo.add_argument("--atualizar-apis", action="store_true", help="Consulta APIs públicas (BCB/IBGE/MDS) e publica")
    parser.add_argument("--competencia", help="Competência alvo AAAA-MM para --atualizar-apis")
    parser.add_argument("--calculado-em", help="Data e hora de cálculo em ISO 8601, com fuso")
    args = parser.parse_args()
    if args.calculado_em:
        calculado_em = datetime.fromisoformat(args.calculado_em)
        if calculado_em.tzinfo is None:
            parser.error("--calculado-em exige fuso horário.")
    else:
        calculado_em = None
    dados = ler_exportacao(args.pasta)
    if args.validar:
        ranking = dados[3]
        print(f"{len(ranking)} municípios, {sum(r[1] is not None for r in ranking.values())} scores disponíveis.")
        return

    import psycopg
    url = os.environ.get("DATABASE_URL")
    if not url:
        parser.error("Configure DATABASE_URL.")

    with psycopg.connect(url) as conn:
        preparar_banco(conn)
        if args.atualizar_apis:
            if not args.competencia:
                parser.error("Informe --competencia AAAA-MM junto com --atualizar-apis.")
            dados, atualizados, proveniencia = atualizar_via_apis(dados, args.competencia)
            edicao = publicar(conn, dados, calculado_em, proveniencia)
            print(f"{atualizados} observações atualizadas via APIs públicas. Edição: {edicao or 'já publicada'}.")
            return
        if args.prever_recalculo or args.publicar_recalculado:
            if args.publicar_recalculado:
                conn.execute("SELECT pg_advisory_xact_lock(2631090)")
            dados, proveniencia, previa = preparar(conn, dados, args.pasta)
            print(json.dumps(previa, ensure_ascii=False), flush=True)
            if args.publicar_recalculado:
                edicao = publicar(conn, dados, calculado_em, proveniencia)
                print(f"Edição publicada: {edicao}" if edicao is not None else "Lote já publicado.")
            return
        if dados[6] > date(2025, 12, 1):
            parser.error("Use --prever-recalculo e --publicar-recalculado para as próximas edições.")
        edicao = publicar(conn, dados, calculado_em)
        importar_apostas(conn)
    ranking = dados[3]
    print(f"{len(ranking)} municípios, {sum(r[1] is not None for r in ranking.values())} scores disponíveis.")
    print(f"Edição publicada: {edicao}" if edicao is not None else "Lote já publicado.")


if __name__ == "__main__":
    main()
