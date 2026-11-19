import contextlib
import json
import os
import re
import sqlite3
import sys
from functools import lru_cache
from pathlib import Path

from flask import Blueprint, Flask, abort, current_app, jsonify, redirect, request, send_from_directory, url_for
from consultas import normalizar, painel, sugestoes

site = Blueprint("kredita_site", __name__)
BACKEND = Path(__file__).resolve().parent
SITE = BACKEND / "kredita-demo" if (BACKEND / "kredita-demo").exists() else BACKEND.parent / "frontend"
SERIES = ("publicado", "simulacao_scr")
RESUMO = """m.codigo_ibge AS id, m.nome, m.uf, m.regiao, s.populacao, s.score,
           s.e1, s.e2, s.e3, s.e4, s.pos_brasil AS position"""
JUNCAO = """FROM municipios m JOIN scores_municipais s USING (codigo_ibge)
           WHERE s.edicao_id = ?"""
LOTE_SCR = """SELECT publicado.lote_id FROM edicoes_score publicado
              WHERE publicado.tipo = 'publicado' AND EXISTS (
                  SELECT 1 FROM edicoes_score simulacao
                  WHERE simulacao.tipo = 'simulacao_scr' AND simulacao.lote_id = publicado.lote_id
              )
              ORDER BY publicado.competencia DESC, publicado.id DESC LIMIT 1"""
CONSULTA_SCR = f"""SELECT s.codigo_ibge, substr(e.competencia, 1, 7) AS mes, s.score,
                          s.e1, s.e2, s.e3, s.e4
                   FROM edicoes_score e JOIN scores_municipais s ON s.edicao_id = e.id
                   WHERE e.tipo = 'simulacao_scr' AND e.lote_id = ({LOTE_SCR})"""


def _dict_row(cursor, row):
    d = {col[0]: row[i] for i, col in enumerate(cursor.description)}
    if "e1" in d and "e4" in d:
        d["eixos"] = [d.pop("e1"), d.pop("e2"), d.pop("e3"), d.pop("e4")]
    return d


class ConexaoSQLite(sqlite3.Connection):
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            return super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.close()

    @contextlib.contextmanager
    def transaction(self):
        if self.in_transaction:
            self.execute("SAVEPOINT kredita_tx")
            try:
                yield
            except Exception:
                self.execute("ROLLBACK TO SAVEPOINT kredita_tx")
                self.execute("RELEASE SAVEPOINT kredita_tx")
                raise
            else:
                self.execute("RELEASE SAVEPOINT kredita_tx")
        else:
            self.execute("BEGIN IMMEDIATE")
            try:
                yield
            except Exception:
                self.rollback()
                raise
            else:
                self.commit()


def conectar_sqlite(url=None, *, como_dict=False):
    alvo = url if url is not None else (
        (current_app.config.get("DATABASE_URL") if current_app else None)
        or os.environ.get("DATABASE_URL")
        or str(BACKEND / "kredita.db")
    )
    if alvo.startswith("sqlite:///"):
        alvo = alvo.removeprefix("sqlite:///")
    conn = sqlite3.connect(alvo, timeout=30, isolation_level=None, factory=ConexaoSQLite)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.create_function("sem_acento", 1, normalizar)
    if como_dict:
        conn.row_factory = _dict_row
    return conn


def conexao():
    try:
        return conectar_sqlite(como_dict=True)
    except sqlite3.Error:
        abort(503, description="Banco SQLite indisponível.")


def consulta_edicao(conn, edicao_id=None):
    try:
        edicao = conn.execute(
            """SELECT id, substr(competencia, 1, 7) AS competencia, versao,
                      calculado_em, publicado_em, lote_id
               FROM edicoes_score WHERE tipo = 'publicado' AND (? IS NULL OR id = ?)
               ORDER BY competencia DESC, id DESC LIMIT 1""",
            (edicao_id, edicao_id),
        ).fetchone()
    except sqlite3.OperationalError:
        edicao = None
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
    if name.endswith(".html"):
        return painel(name.removesuffix(".html"), sys.modules[__name__])
    if not re.fullmatch(r"[a-z-]+\.(css|js|geojson|png)", name):
        abort(404)
    pastas = {"css": "css", "js": "js", "geojson": "mapas", "png": "img"}
    return send_from_directory(SITE / "static" / pastas[name.rsplit(".", 1)[1]], name)


@site.get("/site/sugestoes")
def sugestoes_site():
    with conexao() as conn:
        edicao = consulta_edicao(conn)
        itens = conn.execute(f"SELECT {RESUMO} {JUNCAO} ORDER BY m.nome, m.codigo_ibge",
                             (edicao["id"],)).fetchall()
    return sugestoes(itens)


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
            for row in conn.execute(CONSULTA_SCR):
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


def dados_apostas(conn):
    try:
        estudo = conn.execute(
            """SELECT id, estudo, inicio, fim, metrica, unidade, fonte
               FROM estudos_apostas ORDER BY fim DESC, id DESC LIMIT 1"""
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    if estudo is None:
        return None
    territorios = conn.execute(
        """SELECT uf, valor, margem_pp, populacao_estimada FROM estimativas_apostas
           WHERE estudo_id = ? ORDER BY uf""", (estudo["id"],)
    ).fetchall()
    return dict(**estudo, territorios=territorios)


@site.get("/api/apostas")
def apostas_api():
    with conexao() as conn:
        dados = dados_apostas(conn)
    if dados is None:
        abort(404, description="Nenhum estudo de apostas foi carregado.")
    return jsonify(**dados)


@lru_cache(maxsize=1)
def metodologia_pacote():
    pacote = json.loads((BACKEND / "dados" / "score_kredita.json").read_text(encoding="utf-8-sig"))
    return {"indicadores": pacote["indicadores"], "pesos_finais": pacote["pesos_finais"]}


@site.get("/api/metodologia")
def metodologia_api():
    return jsonify(indicadores=metodologia_pacote()["indicadores"])


@site.get("/api/ranking")
def ranking_api():
    page = max(1, min(1_000_000, request.args.get("pagina", 1, type=int)))
    size = max(1, min(100, request.args.get("limite", 50, type=int)))
    uf = request.args.get("uf", "").upper()
    busca = normalizar(request.args.get("busca", "").strip()[:100])
    filtro = JUNCAO + """ AND s.score IS NOT NULL
        AND (? = '' OR m.uf = ?)
        AND (? = '' OR instr(sem_acento(m.nome || ' ' || m.uf), ?) > 0
             OR m.codigo_ibge = ?)"""
    with conexao() as conn:
        edicao = consulta_edicao(conn)
        params = (edicao["id"], uf, uf, busca, busca, busca)
        total = conn.execute(f"SELECT count(*) AS n {filtro}", params).fetchone()["n"]
        page = min(page, max(1, (total + size - 1) // size))
        items = conn.execute(
            f"""SELECT {RESUMO} {filtro} ORDER BY s.pos_brasil, m.codigo_ibge
                LIMIT ? OFFSET ?""", (*params, size, (page - 1) * size),
        ).fetchall()
    return jsonify(edicao=edicao, municipios=items, total=total, pagina=page, limite=size)


@site.get("/api/municipios/<codigo>")
def detalhe_api(codigo):
    codigo_valido(codigo)
    edicao_id = parametro_edicao()
    with conexao() as conn:
        edicao = consulta_edicao(conn, edicao_id)
        return jsonify(**dados_detalhe(conn, edicao, codigo))


def dados_detalhe(conn, edicao, codigo):
    item = conn.execute(
        f"""SELECT {RESUMO}, s.score_sem_cofator, s.cofator, s.m, s.pos_uf,
                   s.pos_regiao, s.motivo_sem_score {JUNCAO} AND m.codigo_ibge = ?""",
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
           WHERE si.edicao_id = ? AND si.codigo_ibge = ? ORDER BY si.indicador""",
        (edicao["id"], codigo),
    ).fetchall()
    return dict(edicao=edicao, municipio=item, indicadores=indicadores)


def dados_historico(conn, codigo):
    if conn.execute("SELECT 1 FROM municipios WHERE codigo_ibge = ?", (codigo,)).fetchone() is None:
        abort(404, description="Município não encontrado.")
    rows = conn.execute(
        f"""SELECT e.id AS edicao_id, e.tipo, substr(e.competencia, 1, 7) AS competencia,
                  e.versao, e.publicado_em, s.score,
                  s.e1, s.e2, s.e3, s.e4
           FROM edicoes_score e LEFT JOIN scores_municipais s
                ON s.edicao_id = e.id AND s.codigo_ibge = ?
           WHERE e.tipo = 'publicado' OR e.lote_id = ({LOTE_SCR})
           ORDER BY e.competencia, e.id""",
        (codigo,),
    ).fetchall()
    series = {tipo: [] for tipo in SERIES}
    for row in rows:
        series[row.pop("tipo")].append(row)
    return dict(codigo_ibge=codigo, **series)


@site.get("/api/municipios/<codigo>/historico")
def historico_api(codigo):
    codigo_valido(codigo)
    with conexao() as conn:
        consulta_edicao(conn)
        return jsonify(**dados_historico(conn, codigo))


app = Flask(__name__, template_folder=str(SITE / "templates"))
app.jinja_env.filters["mes_br"] = lambda d: f"{d[5:7]}/{d[:4]}" if isinstance(d, str) and len(d) == 7 else d
app.register_blueprint(site)


@app.get("/")
def index():
    return redirect(url_for("kredita_site.arquivos_site"))


@app.get("/municipio/<int:cod_ibge>")
def municipio_detalhe(cod_ibge):
    return redirect(url_for("kredita_site.arquivos_site", name="municipio.html", id=cod_ibge))


def garantir_banco():
    from importar_kredita import ROOT, carregar_apostas_pendentes, ler_exportacao, preparar_banco, publicar

    with conectar_sqlite() as conn:
        preparar_banco(conn)
        if not conn.execute("SELECT 1 FROM edicoes_score WHERE tipo='publicado' LIMIT 1").fetchone():
            publicar(conn, ler_exportacao(ROOT / "dados"))
        carregar_apostas_pendentes(conn)


if __name__ == "__main__":
    garantir_banco()
    app.run()
