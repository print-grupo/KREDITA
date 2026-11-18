import json
import os
import re
import unicodedata
from pathlib import Path

from flask import Blueprint, Flask, abort, current_app, jsonify, redirect, request, send_from_directory, url_for

site = Blueprint("kredita_site", __name__)
BACKEND = Path(__file__).resolve().parent
SITE = BACKEND / "kredita-demo" if (BACKEND / "kredita-demo").exists() else BACKEND.parent / "frontend"
SERIES = ("publicado", "simulacao_scr")
ACENTOS = "áàâãäéèêëíìîïóòôõöúùûüçñ"
SEM_ACENTOS = "aaaaaeeeeiiiiooooouuuucn"
RESUMO = """m.codigo_ibge AS id, m.nome, m.uf, m.regiao, s.populacao, s.score,
           ARRAY[s.e1, s.e2, s.e3, s.e4] AS eixos, s.pos_brasil AS position"""
JUNCAO = """FROM municipios m JOIN scores_municipais s USING (codigo_ibge)
           WHERE s.edicao_id = %s"""
LOTE_SCR = """SELECT publicado.lote_id FROM edicoes_score publicado
              WHERE publicado.tipo = 'publicado' AND EXISTS (
                  SELECT 1 FROM edicoes_score simulacao
                  WHERE simulacao.tipo = 'simulacao_scr' AND simulacao.lote_id = publicado.lote_id
              )
              ORDER BY publicado.competencia DESC, publicado.id DESC LIMIT 1"""


def conexao():
    import psycopg
    from psycopg.rows import dict_row

    url = current_app.config.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        abort(503, description="Conexão com o PostgreSQL não configurada.")
    try:
        return psycopg.connect(url, row_factory=dict_row, connect_timeout=5)
    except psycopg.OperationalError:
        abort(503, description="PostgreSQL indisponível.")


def consulta_edicao(conn, edicao_id=None):
    edicao = conn.execute(
        """SELECT id, to_char(competencia, 'YYYY-MM') AS competencia, versao,
                  calculado_em::text, publicado_em::text, lote_id
           FROM edicoes_score WHERE tipo = 'publicado' AND (%s::bigint IS NULL OR id = %s)
           ORDER BY competencia DESC, id DESC LIMIT 1""",
        (edicao_id, edicao_id),
    ).fetchone()
    if edicao is None:
        if edicao_id is not None:
            abort(404, description="Edição publicada não encontrada.")
        abort(503, description="Nenhuma edição do Kredita foi publicada.")
    return edicao


def codigo_valido(codigo):
    if not re.fullmatch(r"[0-9]{7}", codigo):
        abort(404, description="Município não encontrado.")


def parametro_edicao():
    valor = request.args.get("edicao")
    if valor is None:
        return None
    if not re.fullmatch(r"[1-9][0-9]{0,18}", valor) or int(valor) > 2**63 - 1:
        abort(404, description="Edição publicada não encontrada.")
    return int(valor)


@site.app_errorhandler(404)
@site.app_errorhandler(503)
def erro_api(error):
    if request.path.startswith("/api/"):
        return jsonify(erro=error.description), error.code
    return error


@site.get("/site/")
@site.get("/site/<name>")
def arquivos_site(name="index.html"):
    if not re.fullmatch(r"[a-z-]+\.(html|css|js|geojson|png)", name):
        abort(404)
    return send_from_directory(SITE, name)


@site.get("/api/municipios")
def catalogo():
    with conexao() as conn:
        historico_apenas = request.args.get("simulacao") == "somente"
        edicao_id = parametro_edicao() if historico_apenas else None
        edicao = consulta_edicao(conn, edicao_id)
        items = conn.execute(
            f"SELECT {'m.codigo_ibge AS id' if historico_apenas else RESUMO} {JUNCAO} ORDER BY m.nome, m.codigo_ibge",
            (edicao["id"],),
        ).fetchall()
        if historico_apenas or request.args.get("simulacao") == "1":
            por_codigo = {item["id"]: {} for item in items}
            eixos_por_codigo = {item["id"]: {} for item in items}
            for row in conn.execute(
                f"""SELECT s.codigo_ibge, to_char(e.competencia, 'YYYY-MM') AS mes, s.score,
                          ARRAY[s.e1, s.e2, s.e3, s.e4] AS eixos
                   FROM edicoes_score e JOIN scores_municipais s ON s.edicao_id = e.id
                   WHERE e.tipo = 'simulacao_scr' AND e.lote_id = ({LOTE_SCR})""",
            ):
                por_codigo[row["codigo_ibge"]][row["mes"]] = row["score"]
                eixos_por_codigo[row["codigo_ibge"]][row["mes"]] = row["eixos"]
            if historico_apenas:
                return jsonify(edicao=edicao, municipios=[
                    {"id": item["id"], "pontos": [
                        [mes, score, *eixos_por_codigo[item["id"]][mes]]
                        for mes, score in por_codigo[item["id"]].items()
                    ]} for item in items
                ])
            for item in items:
                item["historico"] = por_codigo[item["id"]]
                item["historico_eixos"] = eixos_por_codigo[item["id"]]
    return jsonify(edicao=edicao, municipios=items)


@site.get("/api/apostas")
def apostas_api():
    with conexao() as conn:
        estudo = conn.execute(
            """SELECT id, estudo, inicio::text, fim::text, metrica, unidade, fonte
               FROM estudos_apostas ORDER BY fim DESC, id DESC LIMIT 1"""
        ).fetchone()
        if estudo is None:
            abort(404, description="Nenhum estudo de apostas foi carregado.")
        territorios = conn.execute(
            """SELECT uf, valor, margem_pp, populacao_estimada FROM estimativas_apostas
               WHERE estudo_id = %s ORDER BY uf""", (estudo["id"],)
        ).fetchall()
    return jsonify(**estudo, territorios=territorios)


@site.get("/api/metodologia")
def metodologia_api():
    pacote = json.loads((BACKEND / "score_kredita.json").read_text(encoding="utf-8-sig"))
    return jsonify(indicadores=pacote["indicadores"])


@site.get("/api/ranking")
def ranking_api():
    page = max(1, min(1_000_000, request.args.get("pagina", 1, type=int)))
    size = max(1, min(100, request.args.get("limite", 50, type=int)))
    uf = request.args.get("uf", "").upper()
    busca = request.args.get("busca", "").strip().lower()[:100]
    busca = "".join(c for c in unicodedata.normalize("NFD", busca) if not unicodedata.combining(c))
    filtro = JUNCAO + """ AND s.score IS NOT NULL
        AND (%s = '' OR m.uf = %s)
        AND (%s = '' OR strpos(lower(translate(m.nome || ' ' || m.uf, %s, %s)), %s) > 0
             OR m.codigo_ibge = %s)"""
    with conexao() as conn:
        edicao = consulta_edicao(conn)
        params = (edicao["id"], uf, uf, busca, ACENTOS + ACENTOS.upper(),
                  SEM_ACENTOS * 2, busca, busca)
        total = conn.execute(f"SELECT count(*) AS n {filtro}", params).fetchone()["n"]
        page = min(page, max(1, (total + size - 1) // size))
        items = conn.execute(
            f"""SELECT {RESUMO} {filtro} ORDER BY s.pos_brasil, m.codigo_ibge
                LIMIT %s OFFSET %s""", (*params, size, (page - 1) * size),
        ).fetchall()
    return jsonify(edicao=edicao, municipios=items, total=total, pagina=page, limite=size)


@site.get("/api/municipios/<codigo>")
def detalhe_api(codigo):
    codigo_valido(codigo)
    edicao_id = parametro_edicao()
    with conexao() as conn:
        edicao = consulta_edicao(conn, edicao_id)
        item = conn.execute(
            f"""SELECT {RESUMO}, s.score_sem_cofator, s.cofator, s.m, s.pos_uf,
                       s.pos_regiao, s.motivo_sem_score {JUNCAO} AND m.codigo_ibge = %s""",
            (edicao["id"], codigo),
        ).fetchone()
        if item is None:
            abort(404, description="Município não encontrado nesta edição.")
        indicadores = conn.execute(
            """SELECT si.indicador, si.nome, si.unidade, o.fonte, o.referencia, o.uf,
                      CASE WHEN si.reaproveitado THEN 'reaproveitado'
                           ELSE o.situacao END AS situacao,
                      o.situacao AS situacao_original, o.valor_bruto, si.valor_usado, si.nota,
                      si.nota_sem_cofator, si.peso
               FROM score_indicadores si JOIN observacoes o ON o.id = si.observacao_id
               WHERE si.edicao_id = %s AND si.codigo_ibge = %s ORDER BY si.indicador""",
            (edicao["id"], codigo),
        ).fetchall()
    return jsonify(edicao=edicao, municipio=item, indicadores=indicadores)


@site.get("/api/municipios/<codigo>/historico")
def historico_api(codigo):
    codigo_valido(codigo)
    with conexao() as conn:
        if conn.execute("SELECT 1 FROM municipios WHERE codigo_ibge = %s", (codigo,)).fetchone() is None:
            abort(404, description="Município não encontrado.")
        rows = conn.execute(
            f"""SELECT e.id AS edicao_id, e.tipo, to_char(e.competencia, 'YYYY-MM') AS competencia,
                      e.versao, e.publicado_em::text, s.score,
                      ARRAY[s.e1, s.e2, s.e3, s.e4] AS eixos
               FROM edicoes_score e LEFT JOIN scores_municipais s
                    ON s.edicao_id = e.id AND s.codigo_ibge = %s
               WHERE e.tipo = 'publicado' OR e.lote_id = ({LOTE_SCR})
               ORDER BY e.competencia, e.id""",
            (codigo,),
        ).fetchall()
    series = {tipo: [] for tipo in SERIES}
    for row in rows:
        series[row.pop("tipo")].append(row)
    return jsonify(codigo_ibge=codigo, **series)


app = Flask(__name__)
app.register_blueprint(site)


@app.get("/")
def index():
    return redirect(url_for("kredita_site.arquivos_site"))


@app.get("/municipio/<int:cod_ibge>")
def municipio_detalhe(cod_ibge):
    return redirect(url_for("kredita_site.arquivos_site", name="municipio.html", id=cod_ibge))


if __name__ == "__main__":
    app.run()
