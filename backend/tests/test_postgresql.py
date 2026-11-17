import csv
import os
import tempfile
import unittest
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import patch

from importar_kredita import (
    BASE,
    atualizar_via_apis,
    checar_metodo,
    digest,
    escolher,
    ler_exportacao,
    preparar,
    publicar,
)

ROOT = Path(__file__).resolve().parents[1]


class ExportacaoEReaproveitamentoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = ler_exportacao(BASE)

    def test_exportacao_e_atualizacao_apis(self):
        _, _, municipios, ranking, observacoes, detalhes, _, historico = self.dados
        self.assertEqual(len(municipios), 5571)
        self.assertEqual(sum(row[1] is not None for row in ranking.values()), 5570)
        self.assertIsNone(ranking["5101837"][1])
        self.assertIsNone(ranking["5101837"][9])
        self.assertEqual(len(historico), 12)
        for indicador, situacao, valor in (
            ("i02", "ausente", None), ("i05", "estimado", None), ("i06", "observado", 0)
        ):
            obs = observacoes[detalhes["5101837", indicador][0]]
            self.assertEqual(obs[-1], situacao)
            if situacao != "estimado":
                self.assertEqual(obs[-2], valor)
        self.assertEqual(observacoes[detalhes["1100015", "i02"][0]][4], "2022")

        def mock_json(url):
            if "TransacoesPixPorMunicipio" in url:
                return {"value": [{"Municipio_Ibge": "1100015", "VL_PagadorPF": 227870000.0}]}
            if "apisidra.ibge.gov.br" in url:
                return [{}, {"D1C": "1100015", "D3C": "2024", "V": "22000"}, {"D1C": "1100015", "D3C": "2025", "V": "22787"}]
            return {}

        novos, n, prov = atualizar_via_apis(self.dados, "2026-01", fetcher=mock_json, fetcher_bytes=lambda _: b"")
        self.assertGreaterEqual(n, 1)
        self.assertIn(("1100015", "i06"), prov[0])
        self.assertEqual(novos[4][novos[5]["1100015", "i09"][0]][4], "2026-01 / população2025")
        self.assertAlmostEqual(novos[4][novos[5]["1100015", "i09"][0]][5], 10000.0)
        self.assertIn(date(2026, 1, 1), novos[7])

    def test_paridade_com_edicao_publicada(self):
        self.assertEqual(checar_metodo(self.dados[1]), date(2025, 12, 1))

    def test_janela_mensal_e_ultima_referencia_anual(self):
        mes = 2026 * 12 + 1
        obs = lambda ref: ("i06", "4106902", None, "CAGED", ref, 0.0, "observado")
        for ref in ("2025-12", "2025-11", "2025-10"):
            self.assertEqual(escolher([obs(ref)], "i06", mes), obs(ref))
        for ref in ("2025-09", "2026-01", "2026-02", "2025", "s/d"):
            self.assertIsNone(escolher([obs(ref)], "i06", mes))
        self.assertEqual(escolher([obs("2022"), obs("2021")], "i02", mes), obs("2022"))
        self.assertEqual(escolher([obs("2025-10"), obs("2025-12")], "i06", mes), obs("2025-12"))

    def test_zero_confirmado_ausencia_e_compatibilidade(self):
        hashes, pacote, municipios, ranking, observacoes, detalhes, _, _ = self.dados
        ids = ["4106902", "3550308", "1100015"]
        municipios = {c: municipios[c] for c in ids}
        ranking = {c: ranking[c] for c in ids}
        detalhes = {k: v for k, v in detalhes.items() if k[0] in ids}
        observacoes = dict(observacoes)
        for codigo in ids:
            h, *valores = detalhes[codigo, "i06"]
            obs = observacoes[h]
            novo_hash = h + "-zero"
            observacoes[novo_hash] = (*obs[:5], 0.0, "observado")
            detalhes[codigo, "i06"] = (novo_hash, *valores)
        dados = hashes, pacote, municipios, ranking, observacoes, detalhes, date(2026, 1, 1), {}
        fonte = observacoes[detalhes[ids[0], "i06"][0]][3]
        unidade = detalhes[ids[0], "i06"][2]

        class FonteHistorica:
            def execute(self, *_):
                return [
                    ("i06", ids[0], None, fonte, "2025-12", 9.0, "observado", unidade),
                    ("i06", ids[1], None, fonte, "2025-11", -2.0, "observado", unidade),
                    ("i06", ids[2], None, "Fonte diferente", "2025-12", 9.0, "observado", unidade),
                    ("i06", None, "RO", fonte, "2025-12", 9.0, "observado", unidade),
                ]

        with tempfile.TemporaryDirectory() as directory:
            pasta = Path(directory)
            with (pasta / "caged_i06_zeros.csv").open("w", encoding="utf8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["codigo_ibge", "situacao"])
                writer.writerows(zip(ids, ["confirmado", "sem_registro", "sem_registro"]))
            with patch("importar_kredita.checar_metodo", return_value=date(2025, 12, 1)):
                novos, proveniencia, previa = preparar(FonteHistorica(), dados, pasta)
        self.assertEqual(proveniencia[0], {(ids[1], "i06")})
        self.assertEqual(proveniencia[1], {ids[0]})
        self.assertEqual(previa["observacoes_reaproveitadas"], {ids[1] + "/i06": "2025-11"})
        self.assertEqual(novos[4][novos[5][ids[0], "i06"][0]][5], 0.0)
        self.assertEqual(novos[4][novos[5][ids[1], "i06"][0]][5], -2.0)
        self.assertIsNone(novos[3][ids[2]][1])


@unittest.skipUnless(os.environ.get("TEST_DATABASE_URL"), "Configure TEST_DATABASE_URL")
class PostgreSQLTest(unittest.TestCase):
    def test_publicacao_e_api(self):
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo

        from app import app

        base = os.environ["TEST_DATABASE_URL"]
        schema = "kredita_test_" + uuid.uuid4().hex
        with psycopg.connect(base, autocommit=True) as admin:
            admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
            self.addCleanup(self.remover_schema, base, schema)
        url = make_conninfo(base, options=f"-c search_path={schema}")
        config_anterior = {key: app.config.get(key) for key in ("TESTING", "DATABASE_URL")}
        self.addCleanup(app.config.update, config_anterior)
        app.config.update(TESTING=True, DATABASE_URL=url)
        client = app.test_client()
        dados = ler_exportacao(ROOT)
        with psycopg.connect(url, autocommit=True) as conn:
            conn.execute((ROOT / "migrations/001_postgresql.sql").read_text(encoding="utf8"))
            self.assertEqual(client.get("/api/municipios").status_code, 503)
            edicao = publicar(conn, dados)
            self.assertIsNotNone(edicao)
            self.assertIsNone(publicar(conn, dados))
            self.assertEqual(conn.execute("SELECT count(*) FROM lotes_importacao").fetchone()[0], 1)

            pagina = client.get("/api/ranking?limite=2&pagina=2").get_json()
            self.assertEqual(pagina["total"], 5570)
            self.assertEqual([item["position"] for item in pagina["municipios"]], [3, 4])
            self.assertEqual(client.get("/api/ranking?busca=%5B").get_json()["total"], 0)
            busca = client.get("/api/ranking?busca=sao+paulo+sp&uf=SP").get_json()
            self.assertIn("3550308", [item["id"] for item in busca["municipios"]])
            catalogo = client.get("/api/municipios?simulacao=1").get_json()
            self.assertEqual(len(catalogo["municipios"]), 5571)
            self.assertEqual(len(catalogo["municipios"][0]["historico"]), 12)
            detalhe = client.get("/api/municipios/5101837").get_json()
            self.assertIsNone(detalhe["municipio"]["score"])
            self.assertIsNone(detalhe["municipio"]["position"])
            ind = {row["indicador"]: row for row in detalhe["indicadores"]}
            self.assertIsNone(ind["i02"]["valor_usado"])
            self.assertEqual(ind["i05"]["situacao"], "estimado")
            self.assertEqual(ind["i06"]["valor_usado"], 0)
            self.assertEqual(ind["i15"]["peso"], 0)
            series = client.get("/api/municipios/1100015/historico").get_json()
            self.assertEqual(len(series["publicado"]), 1)
            self.assertEqual(len(series["simulacao_scr"]), 12)
            self.assertEqual(client.get("/api/municipios/1234567").status_code, 404)
            self.assertEqual(client.get("/").location, "/site/")
            self.assertEqual(client.get("/municipio/5101837").location, "/site/municipio.html?id=5101837")
            with client.get("/site/") as response:
                self.assertEqual(response.status_code, 200)
            self.assertEqual(client.get("/site/base.json").status_code, 404)

            hashes, pacote, municipios, ranking, observacoes, detalhes, periodo, historico = dados
            chave = ("1100015", "i02")
            hash_anterior = detalhes[chave][0]
            hash_novo = digest(b"revisao teste")
            obs = observacoes[hash_anterior]
            revisadas = {**observacoes, hash_novo: (*obs[:-2], obs[-2] + 1, obs[-1])}
            detalhes_novos = {**detalhes, chave: (hash_novo, *detalhes[chave][1:])}
            hash_revisao = {**hashes, "score_kredita.json": hash_novo}
            ranking_invalido = {
                **ranking, chave[0]: (ranking[chave[0]][0], -1, *ranking[chave[0]][2:]),
            }
            with self.assertRaises(psycopg.errors.CheckViolation):
                publicar(conn, (hash_revisao, pacote, municipios, ranking_invalido,
                                 revisadas, detalhes_novos, periodo, historico))
            self.assertEqual(conn.execute("SELECT count(*) FROM lotes_importacao").fetchone()[0], 1)
            revisao = publicar(conn, (hash_revisao, pacote, municipios, ranking, revisadas,
                                     detalhes_novos, periodo, historico))
            valores = conn.execute(
                """SELECT o.valor_bruto FROM score_indicadores si
                   JOIN observacoes o ON o.id = si.observacao_id
                   WHERE si.edicao_id IN (%s, %s) AND si.codigo_ibge = %s AND si.indicador = %s
                   ORDER BY si.edicao_id""",
                (edicao, revisao, *chave),
            ).fetchall()
            self.assertEqual(valores, [(obs[-2],), (obs[-2] + 1,)])
            series = client.get("/api/municipios/1100015/historico").get_json()
            self.assertEqual(len(series["publicado"]), 2)
            self.assertEqual(len(series["simulacao_scr"]), 12)
            for edicao_id, esperado in ((edicao, obs[-2]), (revisao, obs[-2] + 1)):
                resposta = client.get(f"/api/municipios/1100015?edicao={edicao_id}")
                self.assertEqual(resposta.status_code, 200)
                detalhe = resposta.get_json()
                self.assertEqual(detalhe["edicao"]["id"], edicao_id)
                indicador = next(row for row in detalhe["indicadores"] if row["indicador"] == "i02")
                self.assertEqual(indicador["valor_bruto"], esperado)
                self.assertEqual(indicador["referencia"], obs[4])
            simulacao = series["simulacao_scr"][0]["edicao_id"]
            for invalida in (simulacao, "1e2", "9999999999999999999"):
                self.assertEqual(client.get(f"/api/municipios/1100015?edicao={invalida}").status_code, 404)

    @staticmethod
    def remover_schema(base, schema):
        import psycopg
        from psycopg import sql

        with psycopg.connect(base, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


if __name__ == "__main__":
    unittest.main()
