import csv
import io
import json
import math
import re
import unicodedata
from statistics import mean, median
from itertools import combinations
from urllib.parse import urlencode

from flask import Response, abort, render_template, request


PAGINAS = {
    "index": "Visão geral", "ranking": "Ranking municipal", "municipio": "Município",
    "favoritos": "Favoritos", "comparar": "Comparar municípios",
    "guia": "Guia do site", "metodologia": "Metodologia e fontes", "apostas": "Apostas",
}
EIXOS = ("Risco", "Capacidade", "Inclusão", "Demografia")
PORTES = (("small", "Até 20 mil"), ("medium", "Mais de 20 mil até 100 mil"), ("large", "Acima de 100 mil"))
ORDENS = (("", "Maior score"), ("score-asc", "Menor score"), ("name", "Nome (A–Z)"), ("population", "Maior população"))


def numero(valor, casas=1):
    if valor is None:
        return "—"
    return f"{valor:,.{casas}f}".translate(str.maketrans(",.", ".,"))


def normalizar(valor):
    if valor is None:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", str(valor).lower().strip())
                   if not unicodedata.combining(c))


def porte(item):
    populacao = item["populacao"]
    if populacao is None:
        return ""
    return "small" if populacao <= 20000 else "medium" if populacao <= 100000 else "large"


def score_por_eixos(score, notas, eixos):
    if score is None or len(eixos) == 4:
        return score
    valores = [notas[eixo] for eixo in eixos]
    return mean(valores) if all(valor is not None for valor in valores) else None


def classificar(itens, eixos):
    classificados = [{**item, "score": score_por_eixos(item["score"], item["eixos"], eixos)}
                     for item in itens]
    validos = [item for item in classificados if item["score"] is not None]
    if len(eixos) == 4:
        return classificados, sorted(validos, key=lambda item: item["position"])
    validos.sort(key=lambda item: (-item["score"], item["id"]))
    for item in classificados:
        item["position"] = None
    for posicao, item in enumerate(validos, 1):
        item["position"] = posicao
    return classificados, validos


def minimo(valor):
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return None
    return valor if 0 <= valor <= 100 else None


def recorte(itens, filtros):
    busca = normalizar(filtros["busca"])
    return [item for item in itens
            if (not filtros["uf"] or item["uf"] == filtros["uf"])
            and (not filtros["porte"] or porte(item) == filtros["porte"])
            and (busca in normalizar(item["nome"] + " " + item["uf"]) or busca == item["id"])
            and all(limite is None or (nota is not None and nota >= limite)
                    for nota, limite in zip(item["eixos"], filtros["minimos"]))]


def grafico(series, mensal=False, escala=None):
    datas = sorted({data for _, pontos in series for data, _ in pontos})
    if mensal and datas:
        primeiro, ultimo = [int(data[:4]) * 12 + int(data[5:7]) - 1 for data in (datas[0], datas[-1])]
        datas = [f"{mes // 12:04d}-{mes % 12 + 1:02d}" for mes in range(primeiro, ultimo + 1)]
    valores = [valor for _, pontos in series for _, valor in pontos if valor is not None]
    if not valores:
        return None
    baixo_v, alto_v = escala or (min(valores), max(valores))
    passo = next((t for t in (5, 10, 20, 25) if (alto_v - baixo_v) / t <= 4), 25)
    baixo = max(0, math.floor((baixo_v - passo / 2) / passo) * passo)
    alto = min(100, math.ceil((alto_v + passo / 2) / passo) * passo)
    if alto <= baixo:
        baixo, alto = max(0, baixo - 5), min(100, alto + 5)
    span = max(1, len(datas) - 1)
    posicoes = {data: 50.0 if len(datas) == 1 else 100.0 * indice / span for indice, data in enumerate(datas)}
    linhas = []
    for nome, pontos in series:
        mapa = dict(pontos)
        vertices, comandos, iniciar = [], [], True
        for data in datas:
            valor = mapa.get(data)
            if valor is None:
                iniciar = True
                continue
            x, y = posicoes[data], 100.0 * (alto - valor) / (alto - baixo)
            vertices.append((data, valor, x, y))
            comandos.append(f"{'M' if iniciar else 'L'}{x:.2f} {y:.2f}")
            iniciar = False
        linhas.append(dict(nome=nome, vertices=vertices, caminho=" ".join(comandos)))
    meio = next((d for d in datas[1:-1] if 40 <= posicoes[d] <= 60), None) if len(datas) > 2 else None
    marcas_datas = [(datas[0], 50.0)] if len(datas) == 1 else (
        [(datas[0], 0.0)] + ([(meio, posicoes[meio])] if meio else []) + [(datas[-1], 100.0)]
    )
    return dict(linhas=linhas, datas=datas, marcas_datas=marcas_datas, baixo=baixo, alto=alto, posicoes=posicoes)


def pontos(historico, tipo, eixos, revisoes=False):
    return [(f"{row['competencia']} · #{row['edicao_id']}" if revisoes else row["competencia"],
             score_por_eixos(row["score"], row["eixos"], eixos))
            for row in historico[tipo]]


def csv_municipios(pagina, itens):
    output = io.StringIO()
    linhas = csv.writer(output, delimiter=";")
    linhas.writerow(["Código IBGE", "Município", "UF", "População", "Score", "Posição", *EIXOS])
    for item in itens:
        linhas.writerow([item["id"], item["nome"], item["uf"], item["populacao"],
                         item["score"], item["position"], *item["eixos"]])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="kredita-{pagina}.csv"'})


def formulas(ind):
    a, b, c = ([numero(n,2).rstrip("0").rstrip(",") for n in ind["params"]] + [""]*3)[:3]
    menor = f"({a})" if a.startswith("-") else a
    faixa = f"t limitado entre {a} e {b}."
    expressoes = {
        "linear": [("", f"Nota = 100 × (t − {menor}) ÷ ({b} − {menor})", faixa)],
        "inverse": [("", f"Nota = 100 × ({b} − t) ÷ ({b} − {menor})", faixa)],
        "log": [("", f"Nota = 100 × ln(t ÷ {a}) ÷ ln({b} ÷ {a})", faixa)],
        "loginverse": [("", f"Nota = 100 × ln({b} ÷ t) ÷ ln({b} ÷ {a})", faixa)],
        "signed": [("", f"Nota = 50 + 50 × x ÷ {a}", "Nota limitada entre 0 e 100.")],
        "centerlog": [(f"t ≤ {b}", f"Nota = 50 × ln(t ÷ {a}) ÷ ln({b} ÷ {a})", ""),
                      (f"t > {b}", f"Nota = 50 + 50 × ln(t ÷ {b}) ÷ ln({c} ÷ {b})", f"t limitado entre {a} e {c}.")],
        "informality": [(f"x ≤ {b}", f"Nota = 30 + 20 × (x − {a}) ÷ ({b} − {a})", "De 30 a 50."),
                        (f"x > {b}", f"Nota = 50 + 50 × (x − {b}) ÷ ({c} − {b})", "De 50 a 100.")],
        "none": [("", "A população é exibida em habitantes e tem peso zero no score.", "")],
    }
    return expressoes[ind["kind"]]


def url_com(**mudancas):
    return request.path + "?" + urlencode(dict(request.args.to_dict(flat=False), **mudancas), doseq=True)


def serie_scr(conn, lote_scr, codigos, eixos):
    if not codigos:
        return []
    expr = ("s.score" if len(eixos) == 4
            else f"CASE WHEN s.score IS NOT NULL THEN ({' + '.join(f's.e{i + 1}' for i in eixos)}) / {len(eixos)}.0 END")
    filtro, param = (("s.codigo_ibge = ?", codigos[0]) if len(codigos) == 1
                     else ("s.codigo_ibge IN (SELECT value FROM json_each(?))", json.dumps(codigos)))
    rows = conn.execute(
        f"""SELECT substr(e.competencia, 1, 7) AS mes, AVG({expr}) AS media
            FROM edicoes_score e JOIN scores_municipais s ON s.edicao_id = e.id
            WHERE e.tipo = 'simulacao_scr' AND e.lote_id = ({lote_scr}) AND {filtro}
            GROUP BY mes ORDER BY mes""",
        (param,),
    ).fetchall()
    return [(row["mes"], row["media"]) for row in rows]


def codigos_validos(chave):
    return list(dict.fromkeys(c for c in request.args.get(chave, "").split(",")
                              if re.fullmatch(r"[0-9]{7}", c)))


def buscar_sugestoes(itens, texto):
    busca = normalizar(texto)
    if not busca:
        return []
    encontrados = [item for item in itens if busca == item["id"] or busca in normalizar(item["nome"] + " " + item["uf"])]
    encontrados.sort(key=lambda item: (
        busca not in (item["id"], normalizar(item["nome"])),
        not normalizar(item["nome"]).startswith(busca), normalizar(item["nome"])))
    return encontrados[:8]


def ordenar_itens(itens, ordem, *, padrao_score=False):
    if ordem == "name":
        itens.sort(key=lambda item: (normalizar(item["nome"]), item["position"] or 10**9))
    elif ordem == "population":
        itens.sort(key=lambda item: (-(item["populacao"] or 0), item["position"] or 10**9, normalizar(item["nome"])))
    elif ordem == "score-asc":
        itens.sort(key=lambda item: (item["score"] if item["score"] is not None else 10**9, item["position"] or 10**9, normalizar(item["nome"])))
    elif padrao_score:
        itens.sort(key=lambda item: (-(item["score"] if item["score"] is not None else -1), normalizar(item["nome"])))


def sugestoes(itens):
    encontrados = buscar_sugestoes(itens, request.args.get("busca", "")[:100])
    return render_template("_sugestoes.html", itens=encontrados, favoritos=codigos_validos("favoritos"),
                           selecionar=request.args.get("selecionar") == "1")


def painel(pagina, backend):
    if pagina not in PAGINAS:
        abort(404)
    args = request.args
    solicitados = ",".join(args.getlist("eixos")).split(",")
    eixos = tuple(i for i in range(4) if str(i + 1) in solicitados) or tuple(range(4))
    eixos_url = ",".join(str(i + 1) for i in eixos)
    filtros = dict(busca=args.get("busca", "")[:100], uf=args.get("uf", "").upper(),
                   porte=args.get("porte", ""), ordem=args.get("ordem", ""),
                   minimos=[minimo(args.get(f"min{i + 1}")) for i in range(4)])
    favoritos = codigos_validos("favoritos")
    comparar = codigos_validos("comparar")[:3]
    contexto = dict(pagina=pagina, paginas=PAGINAS, titulo=PAGINAS[pagina], eixos=EIXOS, ativos=eixos,
                    eixos_url=eixos_url, filtros=filtros, favoritos=favoritos, comparar=comparar,
                    portes=PORTES, ordens=ORDENS,
                    score_label="Score geral" if len(eixos) == 4 else "Score dos eixos selecionados",
                    numero=numero, url_pagina=request.path, args=args, grafico=grafico,
                    paginar=lambda n: url_com(pagina=n), exportar=lambda: url_com(exportar="csv"),
                    selecionado=None)
    if pagina == "metodologia":
        pacote = backend.metodologia_pacote()
        contexto.update(indicadores=pacote["indicadores"], pesos=pacote["pesos_finais"], formulas=formulas,
                        frequencias=("Mensal", "Censitária", "Mensal", "Censitária", "Mensal", "Mensal",
                                     "Censitária", "Mensal", "Mensal", "Mensal", "Mensal", "Censitária",
                                     "Anual", "Censitária", "Anual", "Conforme publicação"))
    if pagina in ("apostas", "index", "ranking", "municipio", "favoritos", "comparar"):
        with backend.conexao() as conn:
            apostas = backend.dados_apostas(conn) if pagina in ("apostas", "index") else None
            if pagina in ("apostas", "index"):
                contexto["apostas"] = apostas
            if pagina in ("index", "ranking", "municipio", "favoritos", "comparar"):
                edicao = backend.consulta_edicao(conn)
                catalogo = backend.catalogo_publicado(conn, edicao)
                catalogo, ranking = classificar(catalogo, eixos)
                por_codigo = {item["id"]: item for item in catalogo}
                selecionado = por_codigo.get(args.get("id"))
                if pagina == "index" and selecionado:
                    filtros["uf"] = selecionado["uf"]
                itens = recorte(ranking, filtros)
                contexto.update(edicao=edicao, selecionado=selecionado, ufs=sorted({item["uf"] for item in catalogo}),
                                sugestoes=buscar_sugestoes(catalogo, filtros["busca"]))
                if pagina == "ranking":
                    ordenar_itens(itens, filtros["ordem"])
                    paginas = max(1, (len(itens) + 49) // 50)
                    indice = min(paginas, max(1, args.get("pagina", 1, type=int)))
                    contexto.update(itens=itens[(indice - 1)*50:indice*50], total=len(itens),
                                    indice=indice, total_paginas=paginas)
                if pagina == "index":
                    codigos = [selecionado["id"]] if selecionado else [item["id"] for item in itens]
                    historico = serie_scr(conn, backend.LOTE_SCR, codigos, eixos)
                    contexto.update(total=len(itens), media=mean(i["score"] for i in itens) if itens else None,
                                    lista_uf=[i for i in catalogo if filtros["uf"] and i["uf"] == filtros["uf"]],
                                    mapa=[[i["id"], i["score"]] for i in itens],
                                    exemplos=itens[:5],
                                    perfil_atual=selecionado or ({"eixos": [mean(i["eixos"][e] for i in itens) if e in eixos else None
                                                                     for e in range(4)]} if itens else None),
                                    historico=grafico([("Simulação SCR", historico)], mensal=True),
                                    aposta=next((row for row in (apostas or {}).get("territorios", [])
                                                 if row["uf"] == (filtros["uf"] or "BR")), None))
                if pagina == "municipio":
                    if selecionado is None:
                        abort(404)
                    detalhe = backend.dados_detalhe(conn, edicao, selecionado["id"])
                    historico = backend.dados_historico(conn, selecionado["id"])
                    contexto.update(detalhe=detalhe, publicado=grafico([("Edições publicadas", pontos(historico, "publicado", eixos, True))]),
                                    scr=grafico([("Simulação SCR", pontos(historico, "simulacao_scr", eixos))], mensal=True),
                                    historico_edicoes=historico["publicado"])
                    edicoes = {row["edicao_id"]: row for row in historico["publicado"]}
                    ids_edicao = list(edicoes)
                    origem = args.get("origem", ids_edicao[-2] if len(ids_edicao) > 1 else None, type=int)
                    destino = args.get("destino", ids_edicao[-1] if ids_edicao else None, type=int)
                    contexto.update(origem=origem, destino=destino)
                    if origem != destino and origem in edicoes and destino in edicoes:
                        anterior = backend.dados_detalhe(conn, backend.consulta_edicao(conn, origem), selecionado["id"])
                        posterior = backend.dados_detalhe(conn, backend.consulta_edicao(conn, destino), selecionado["id"])
                        indicadores = {row["indicador"]: row for row in anterior["indicadores"]}
                        mudancas = [(indicadores[row["indicador"]], row) for row in posterior["indicadores"]
                                    if row["indicador"] in indicadores and indicadores[row["indicador"]] != row]
                        contexto.update(mudancas=mudancas, score_atual=score_por_eixos(edicoes[destino]["score"], edicoes[destino]["eixos"], eixos),
                                        score_anterior=score_por_eixos(edicoes[origem]["score"], edicoes[origem]["eixos"], eixos),
                                        contribuicoes=[
                            (EIXOS[e], (edicoes[destino]["eixos"][e] - edicoes[origem]["eixos"][e])/len(eixos))
                            for e in eixos if edicoes[destino]["eixos"][e] is not None and edicoes[origem]["eixos"][e] is not None])
                if pagina in ("favoritos", "comparar"):
                    codigos = favoritos if pagina == "favoritos" else comparar
                    itens = [por_codigo[c] for c in codigos if c in por_codigo]
                    if pagina == "favoritos":
                        contexto["total_favoritos"] = len(itens)
                        if filtros["busca"]:
                            itens = recorte(itens, dict(filtros, uf="", porte="", minimos=[None]*4))
                        ordenar_itens(itens, filtros["ordem"], padrao_score=True)
                    contexto["itens"] = itens
                if pagina == "comparar":
                    tipo = "publicado" if args.get("serie") == "publicado" else "simulacao_scr"
                    por_porte = args.get("referencia") == "porte"
                    perfis, sobrepostas = [], []
                    historias = {item["id"]: backend.dados_historico(conn, item["id"]) for item in itens}
                    valores = [valor for h in historias.values() for tipo_hist in h if tipo_hist != "codigo_ibge"
                               for _, valor in pontos(h, tipo_hist, eixos) if valor is not None]
                    escala = (min(valores), max(valores)) if valores else None
                    for item in itens:
                        h = historias[item["id"]]
                        grupo = [i["score"] for i in ranking if (porte(i) == porte(item) and porte(item)
                                 if por_porte else i["uf"] == item["uf"])]
                        ponto = pontos(h, tipo, eixos)
                        sobrepostas.append((item["nome"], list(dict(ponto).items())))
                        perfis.append(dict(item=item, referencia=median(grupo) if grupo else None, grupo=len(grupo),
                                           publicado=grafico([(item["nome"], pontos(h, "publicado", eixos, True))], escala=escala),
                                           scr=grafico([(item["nome"], pontos(h, "simulacao_scr", eixos))], mensal=True, escala=escala)))
                    diferencas = {}
                    for data in sorted({data for _, serie in sobrepostas for data, _ in serie}):
                        valores_mes = [(nome, dict(serie).get(data)) for nome, serie in sobrepostas]
                        pares = [
                            f"{nome} − {outro_nome} ({valor - outro_valor:+.1f} pontos)".replace(".", ",")
                            for (nome, valor), (outro_nome, outro_valor) in combinations(valores_mes, 2)
                            if valor is not None and outro_valor is not None
                        ]
                        diferencas[data] = {"valores": valores_mes, "pares": pares}
                    contexto.update(perfis=perfis, diferencas=diferencas,
                                    sobreposto=grafico(sobrepostas, mensal=tipo != "publicado")
                                    if len(sobrepostas) >= 2 else None)
                if args.get("exportar") == "csv" and pagina in ("index", "ranking", "favoritos", "comparar"):
                    return csv_municipios(pagina, itens)
    parcial = request.headers.get("X-Kredita-Parcial")
    response = Response(render_template(f"{pagina}.html", parcial=bool(parcial), **contexto))
    response.cache_control.no_cache = True
    response.cache_control.private = True
    response.vary.add("X-Kredita-Parcial")
    return response
