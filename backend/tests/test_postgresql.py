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
    atualizacao_guiada,
    checar_metodo,
    digest,
    escolher,
    executar_atualizacao,
    ler_exportacao,
    preparar,
    publicar,
)

ROOT = Path(__file__).resolve().parents[1]


class AtualizacaoGuiadaTest(unittest.TestCase):
    def test_confirmacao_cancelamento_e_base_alterada(self):
        lote = ({"hash": "original"}, None, None, {"1": [100, 50]})
        previa = dict(competencia="2026-01", observacoes_atualizadas=1,
                      observacoes_reaproveitadas=2, municipios_ganharam_score=0,
                      municipios_perderam_score=0)
        dados = (None, None, {})
        for resposta, mudou in (("", False), ("PUBLICAR", False), ("PUBLICAR", True)):
            with self.subTest(resposta=resposta, mudou=mudou):
                conn = unittest.mock.MagicMock()
                revisado = ({"hash": "alterado"}, *lote[1:]) if mudou else lote
                with patch("builtins.input", return_value=resposta), patch("builtins.print"), \
                     patch("importar_kredita.coletar_fontes_publicas", return_value={}) as coletar, \
                     patch("importar_kredita.atualizar_via_apis",
                           side_effect=[(lote, None, previa), (revisado, None, previa)]), \
                     patch("importar_kredita.publicar", return_value=2) as publicar_lote:
                    if mudou:
                        with self.assertRaisesRegex(ValueError, "base mudou"):
                            atualizacao_guiada(conn, dados, "2026-01", None)
                    else:
                        atualizacao_guiada(conn, dados, "2026-01", None)
                    coletar.assert_called_once()
                    if resposta and not mudou:
                        publicar_lote.assert_called_once_with(conn, lote, None, None)
                    else:
                        publicar_lote.assert_not_called()


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

        base_caged = observacoes[detalhes["1100015", "i06"][0]]
        conn = unittest.mock.Mock()
        conn.execute.side_effect = [[(*base_caged[:4], "2025-12", 0.0, "observado",
                                      detalhes["1100015", "i06"][2])], []]
        novos, prov, previa = atualizar_via_apis(
            conn, self.dados, "2026-01", fetcher=mock_json, fetcher_bytes=lambda _: b""
        )
        self.assertGreaterEqual(previa["observacoes_atualizadas"], 1)
        self.assertIn(("1100015", "i06"), prov[0])
        self.assertEqual(novos[4][novos[5]["1100015", "i06"][0]][5], 0)
        self.assertEqual(novos[4][novos[5]["1100015", "i09"][0]][4], "2026-01 / população2025")
        self.assertAlmostEqual(novos[4][novos[5]["1100015", "i09"][0]][5], 10000.0)
        self.assertEqual(novos[7], {})
        self.assertIsNone(novos[3]["1100015"][1])

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


class PostgreSQLTest(unittest.TestCase):
    def test_publicacao_e_api(self):
        import contextlib
        import sqlite3

        from app import app, conectar_sqlite
        from importar_kredita import preparar_banco

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        url = str(Path(temp_dir.name) / "kredita_test.db")
        config_anterior = {key: app.config.get(key) for key in ("TESTING", "DATABASE_URL")}
        self.addCleanup(app.config.update, config_anterior)
        app.config.update(TESTING=True, DATABASE_URL=url)
        client = app.test_client()
        dados = ler_exportacao(ROOT)
        with contextlib.closing(conectar_sqlite(url)) as conn:
            conn.execute((ROOT / "migrations/001_postgresql.sql").read_text(encoding="utf8"))
            conn.execute("INSERT INTO municipios VALUES ('0000001', 'Teste', 'SP', 'Sudeste')")
            preparar_banco(conn)
            preparar_banco(conn)
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO municipios VALUES (NULL, 'Teste', 'SP', 'Sudeste')")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE municipios SET codigo_ibge=NULL WHERE codigo_ibge='0000001'")
            conn.execute("DELETE FROM municipios WHERE codigo_ibge='0000001'")
            self.assertEqual(client.get("/api/municipios").status_code, 503)
            edicao = publicar(conn, dados)
            self.assertIsNotNone(edicao)
            self.assertIsNone(publicar(conn, dados))
            self.assertEqual(conn.execute("SELECT count(*) FROM lotes_importacao").fetchone()[0], 1)
            for invalida in ("2026-99-01", "2026-00-01", "0000-01-01", "2026/01/01"):
                with self.subTest(competencia=invalida), self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """INSERT INTO edicoes_score(lote_id,competencia,versao,configuracao,tipo)
                           SELECT lote_id,?,versao,configuracao,tipo FROM edicoes_score WHERE id=?""",
                        (invalida, edicao),
                    )
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("UPDATE edicoes_score SET competencia=? WHERE id=?", (invalida, edicao))

            pagina = client.get("/api/ranking?limite=2&pagina=2").get_json()
            self.assertEqual(pagina["total"], 5570)
            self.assertEqual([item["position"] for item in pagina["municipios"]], [3, 4])
            self.assertEqual(client.get("/api/ranking?busca=%5B").get_json()["total"], 0)
            busca = client.get("/api/ranking?busca=sao+paulo+sp&uf=SP").get_json()
            self.assertIn("3550308", [item["id"] for item in busca["municipios"]])
            catalogo = client.get("/api/municipios?simulacao=1").get_json()
            self.assertEqual(len(catalogo["municipios"]), 5571)
            self.assertEqual(len(catalogo["municipios"][0]["historico"]), 12)
            compacto = client.get(f"/api/municipios?simulacao=somente&edicao={edicao}").get_json()
            antigo = catalogo["municipios"][0]
            primeiro = compacto["municipios"][0]
            self.assertEqual(primeiro["id"], antigo["id"])
            self.assertEqual({mes: score for mes, score, *_ in primeiro["pontos"]}, antigo["historico"])
            self.assertEqual({mes: eixos for mes, _, *eixos in primeiro["pontos"]}, antigo["historico_eixos"])
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
            for pagina in ("ranking", "municipio", "favoritos", "comparar", "guia", "metodologia", "apostas"):
                with self.subTest(pagina=pagina):
                    resposta = client.get(f"/site/{pagina}.html?id=4106902&favoritos=4106902&comparar=4106902,3550308")
                    self.assertEqual(resposta.status_code, 200)
                    self.assertIn(b'id="conteudo"', resposta.data)
            parcial = client.get("/site/ranking.html?uf=SP&busca=sao+paulo&eixos=1,2&min3=0",
                                 headers={"X-Kredita-Parcial": "1"})
            self.assertEqual(parcial.status_code, 200)
            self.assertIn("São Paulo".encode(), parcial.data)
            self.assertNotIn(b"<!doctype", parcial.data)
            self.assertIn("X-Kredita-Parcial", parcial.vary)
            csv = client.get("/site/favoritos.html?favoritos=4106902&exportar=csv")
            self.assertEqual(csv.mimetype, "text/csv")
            self.assertIn(b"4106902", csv.data)
            self.assertEqual(client.get("/site/base.json").status_code, 404)

            hashes, pacote, municipios, ranking, observacoes, detalhes, periodo, historico = dados
            chave = ("1100015", "i02")
            hash_anterior = detalhes[chave][0]
            hash_novo = digest(b"revisao teste")
            obs = observacoes[hash_anterior]
            revisadas = {**observacoes, hash_novo: (*obs[:4], "2021", obs[-2] + 1, obs[-1])}
            detalhes_novos = {**detalhes, chave: (hash_novo, *detalhes[chave][1:])}
            hash_revisao = {**hashes, "score_kredita.json": hash_novo}
            ranking_invalido = {
                **ranking, chave[0]: (ranking[chave[0]][0], -1, *ranking[chave[0]][2:]),
            }
            with self.assertRaises(sqlite3.IntegrityError):
                publicar(conn, (hash_revisao, pacote, municipios, ranking_invalido,
                                 revisadas, detalhes_novos, periodo, historico))
            self.assertEqual(conn.execute("SELECT count(*) FROM lotes_importacao").fetchone()[0], 1)
            revisao = publicar(conn, (hash_revisao, pacote, municipios, ranking, revisadas,
                                     detalhes_novos, periodo, historico),
                               proveniencia=(set(), {"5101837"}, {}))
            marcacoes = conn.execute(
                """SELECT edicao_id, indicador, zero_i06_confirmado FROM score_indicadores
                   WHERE edicao_id IN (?, ?) AND codigo_ibge='5101837' AND indicador IN ('i05', 'i06')
                   ORDER BY edicao_id, indicador""",
                (edicao, revisao),
            ).fetchall()
            self.assertEqual(marcacoes, [(edicao, "i05", False), (edicao, "i06", False),
                                        (revisao, "i05", False), (revisao, "i06", True)])
            valores = conn.execute(
                """SELECT o.valor_bruto FROM score_indicadores si
                   JOIN observacoes o ON o.id = si.observacao_id
                   WHERE si.edicao_id IN (?, ?) AND si.codigo_ibge = ? AND si.indicador = ?
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
                self.assertEqual(indicador["referencia"], obs[4] if edicao_id == edicao else "2021")
            simulacao = series["simulacao_scr"][0]["edicao_id"]
            for invalida in (simulacao, "1e2", "9999999999999999999"):
                self.assertEqual(client.get(f"/api/municipios/1100015?edicao={invalida}").status_code, 404)

            def coletar(valor):
                return {"referencias": {"i09": "2026-01"}, "i09": {"1100015": valor}}

            self.assertRaises(ValueError, atualizar_via_apis, conn, dados, "2025-12")
            with patch("importar_kredita.coletar_fontes_publicas", return_value={"referencias": {}}):
                with self.assertRaisesRegex(ValueError, "observações válidas"):
                    atualizar_via_apis(conn, dados, "2026-01")
            with patch("importar_kredita.coletar_fontes_publicas", return_value=coletar(100)):
                ligado, previa = executar_atualizacao(conn, dados, "2026-01", coletar(100), None)
                self.assertEqual(previa["observacoes_atualizadas"], 1)
                self.assertEqual(conn.execute("SELECT count(*) FROM lotes_importacao").fetchone()[0], 2)
                executar_atualizacao(conn, dados, "2026-01", coletar(100), None,
                                     gravar=True, esperada=(ligado[0], previa))
                atual = conn.execute("SELECT max(id) FROM edicoes_score WHERE tipo='publicado'").fetchone()[0]
                self.assertIsNotNone(atual)
                repetido, repetida, _ = atualizar_via_apis(conn, dados, "2026-01")
                self.assertIsNone(publicar(conn, repetido, proveniencia=repetida))
            with patch("importar_kredita.coletar_fontes_publicas", return_value=coletar(101)):
                corrigido, proveniencia, _ = atualizar_via_apis(conn, dados, "2026-01")
                self.assertIsNotNone(publicar(conn, corrigido, proveniencia=proveniencia))
            detalhe = client.get(f"/api/municipios/1100015?edicao={atual}").get_json()
            reaproveitado = next(row for row in detalhe["indicadores"] if row["indicador"] == "i02")
            self.assertEqual(reaproveitado["situacao"], "reaproveitado")
            self.assertEqual(reaproveitado["referencia"], "2022")
            final = client.get("/api/municipios/1100015/historico").get_json()
            self.assertEqual(len(final["publicado"]), 4)
            self.assertEqual(final["simulacao_scr"], series["simulacao_scr"])


if __name__ == "__main__":
    unittest.main()
