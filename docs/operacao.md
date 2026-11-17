# Kredita com PostgreSQL

O `importar_kredita.py` aplica as migrações, valida `score_kredita.json`, publica a edição, a série histórica SCR e os dados de apostas no PostgreSQL e também pode atualizar indicadores via APIs públicas. O `app.py` (Flask) serve o site e a API.

## Rodar localmente

Com Python e PostgreSQL instalados, crie um banco vazio chamado `kredita`. No PowerShell, use a URL do seu banco local.

```powershell
python -m pip install -r requirements.txt
$env:DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/kredita'
python importar_kredita.py --validar
python importar_kredita.py
python app.py
```

Abra [o site local](http://127.0.0.1:5000/site/).

## Rodar com Docker

Na raiz do repositório, com Docker Compose disponível, defina `KREDITA_DB_PASSWORD`:

```powershell
$env:KREDITA_DB_PASSWORD = [guid]::NewGuid().ToString('N')
$env:KREDITA_HTTP_BIND = '127.0.0.1'
docker compose up -d --build --wait
```

Abra [o painel Docker](http://127.0.0.1:8788/site/).

## Atualizar dados via APIs públicas ou novas edições

Para atualizar os dados mensais consultando diretamente a API aberta do Banco Central (Olinda Pix) e recalculando os scores localmente:

```powershell
python importar_kredita.py --atualizar-apis --competencia 2026-01
```

Para publicar uma nova pasta exportada do Colab com reaproveitamento de até 3 competências anteriores e checagem de zeros do CAGED (`caged_i06_zeros.csv`):

```powershell
python importar_kredita.py caminho-da-nova-edicao --prever-recalculo
python importar_kredita.py caminho-da-nova-edicao --publicar-recalculado
```

## API

- `GET /api/ranking?pagina=1&limite=50&uf=SP&busca=` retorna o ranking paginado.
- `GET /api/municipios` retorna o catálogo e o resumo da edição atual (`?simulacao=1` inclui a série mensal SCR).
- `GET /api/municipios/1100015` retorna o score e a auditoria dos indicadores (`?edicao=1` consulta uma edição publicada específica).
- `GET /api/municipios/1100015/historico` retorna as edições publicadas e a simulação SCR em séries distintas.
- `GET /api/apostas` retorna o estudo territorial mais recente e suas estimativas por abrangência.
- `GET /api/metodologia` retorna o dicionário dos indicadores.

## Testes

```powershell
$env:TEST_DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/kredita_teste'
python -m unittest discover -s tests
```
