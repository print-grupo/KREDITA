# Kredita com SQLite

O `importar_kredita.py` cria o esquema SQLite em modo WAL (`kredita.db`), valida `backend/dados/score_kredita.json` e lê as estimativas em `backend/dados/apostas.json`, publica a edição, a série histórica SCR e os dados de apostas e também pode atualizar indicadores via APIs públicas. O `app.py` (Flask + Jinja) serve o site e a API.

## Rodar localmente

Com Python instalado, basta instalar o Flask, importar a base e iniciar o servidor (por padrão usa `kredita.db` na pasta do backend, ou o caminho definido em `DATABASE_URL`):

```powershell
python -m pip install -r requirements.txt
python importar_kredita.py --validar
python importar_kredita.py
python app.py
```

Abra [o site local](http://127.0.0.1:5000/site/).

## Rodar com Docker

Na raiz do repositório, com Docker Compose disponível:

```powershell
$env:KREDITA_HTTP_BIND = '127.0.0.1'
docker compose up -d --build --wait
```

Abra [o painel Docker](http://127.0.0.1:8788/site/). O arquivo do banco SQLite fica persistido no volume Docker `data` (`/app/data/kredita.db`).

## Atualizar dados via APIs públicas ou novas edições

Para o fluxo guiado de atualização via APIs públicas (IBGE SIDRA, BCB Pix, BCB Agências, MDS CadÚnico, BCB SCR e ESTBAN), que mostra a prévia e pede confirmação antes de publicar:

```powershell
python importar_kredita.py --guiado
```

Ou por linha de comando:

```powershell
python importar_kredita.py --atualizar-apis --competencia 2026-01
python importar_kredita.py --atualizar-apis --competencia 2026-01 --publicar
```

Para publicar uma nova pasta exportada com reaproveitamento de até 3 competências anteriores e checagem de zeros do CAGED (`caged_i06_zeros.csv`):

```powershell
python importar_kredita.py caminho-da-nova-edicao --prever-recalculo
python importar_kredita.py caminho-da-nova-edicao --publicar-recalculado
```

Os scripts SQL ficam em `backend/banco_de_dados/` e são aplicados na ordem dos nomes.

## API

- `GET /api/ranking?pagina=1&limite=50&uf=SP&busca=` retorna o ranking paginado.
- `GET /api/municipios` retorna o catálogo e o resumo da edição atual (`?simulacao=1` ou `?simulacao=somente` inclui a série mensal SCR).
- `GET /api/municipios/1100015` retorna o score e a auditoria dos indicadores (`?edicao=1` consulta uma edição publicada específica).
- `GET /api/municipios/1100015/historico` retorna as edições publicadas e a simulação SCR em séries distintas.
- `GET /api/apostas` retorna o estudo territorial mais recente e suas estimativas por abrangência.
- `GET /api/metodologia` retorna o dicionário dos indicadores.

## Testes

```powershell
python -m unittest discover -s tests -v
```
