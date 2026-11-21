# Guia de instalação e operação

Este guia explica como executar o KREDITA localmente, atualizar os dados e consultar os recursos técnicos da aplicação.

Para utilizar a plataforma sem instalar o projeto, acesse o [site do KREDITA](https://kredita.duckdns.org/).

## 1. Instalação com Docker

O Docker prepara o ambiente e instala as dependências da aplicação. Neste método, não é necessário instalar Python ou SQLite separadamente.

### Pré-requisitos

- [Git](https://git-scm.com/downloads) instalado.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução, utilizando containers Linux.
- Internet disponível para baixar o projeto e preparar o ambiente.

Os comandos abaixo utilizam **PowerShell no Windows**.

### Passo 1 — Baixar o projeto

```powershell
git clone --branch feat/retrabalho-site https://github.com/print-grupo/KREDITA.git
```

Cria a pasta `KREDITA` com a versão utilizada neste guia.

> Após a integração da versão final, a branch indicada neste comando deverá ser revisada.

### Passo 2 — Entrar na pasta

```powershell
cd KREDITA
```

Os próximos comandos devem ser executados nessa pasta, onde está o arquivo `compose.yaml`.

### Passo 3 — Configurar o acesso local

```powershell
$env:KREDITA_HTTP_BIND = "127.0.0.1"
```

Limita o acesso ao próprio computador. Essa variável vale para a sessão atual do PowerShell.

### Passo 4 — Preparar e iniciar

```powershell
docker compose up -d --build
```

Prepara a imagem, executa a importação dos dados e inicia a aplicação em segundo plano. A primeira execução pode demorar devido aos downloads.

### Passo 5 — Acessar

Abra no navegador:

**[http://127.0.0.1:8788/site/](http://127.0.0.1:8788/site/)**

### Passo 6 — Encerrar quando necessário

```powershell
docker compose down
```

Encerra a aplicação, preservando o volume do banco.

> Não acrescente `-v` se quiser manter os dados: essa opção remove os volumes associados.

## 2. O que acontece na inicialização?

O ambiente Docker:

1. Instala as dependências Python.
2. Executa `importar_kredita.py`.
3. Valida e importa a base disponibilizada no projeto.
4. Inicia o Gunicorn para disponibilizar a aplicação Flask.

O SQLite fica em `/app/data/kredita.db`, armazenado no volume persistente `data`.

A carga inicial utiliza `backend/dados/score_kredita.json`. Não é necessário executar o Google Colab nem criar as tabelas manualmente.

Essa inicialização não realiza uma nova coleta completa das fontes públicas. A atualização dos dados é uma operação separada.

## 3. Comandos de acompanhamento

Execute os comandos abaixo na raiz do projeto.

### Verificar o serviço

```powershell
docker compose ps
```

Mostra o estado do container e a porta utilizada.

### Consultar os registros

```powershell
docker compose logs --tail=100 web
```

Exibe as mensagens recentes da importação e do servidor.

Para acompanhar continuamente:

```powershell
docker compose logs -f web
```

Pressione **Ctrl + C** para sair do acompanhamento. Isso não encerra a aplicação.

### Iniciar novamente

Com o Docker Desktop aberto, configure o acesso local na sessão do PowerShell:

```powershell
$env:KREDITA_HTTP_BIND = "127.0.0.1"
```

Depois execute:

```powershell
docker compose up -d
```

Se houver alterações nas dependências ou nos arquivos incorporados à imagem, utilize novamente:

```powershell
docker compose up -d --build
```

> Reconstruir a imagem não substitui o processo de publicação de uma nova edição dos dados.

## 4. Execução com Python

Esta alternativa é destinada ao desenvolvimento local, sem Docker. Utilize Python 3.12 para acompanhar a versão configurada na imagem do projeto.

Os comandos abaixo partem da raiz da pasta `KREDITA`.

### Criar o ambiente virtual

```powershell
python -m venv .venv
```

### Instalar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

### Entrar no backend

```powershell
cd backend
```

### Validar a base

```powershell
..\.venv\Scripts\python.exe importar_kredita.py --validar
```

Confere a base de integração sem publicá-la.

### Preparar o banco e importar os dados

```powershell
..\.venv\Scripts\python.exe importar_kredita.py
```

### Iniciar a aplicação

```powershell
..\.venv\Scripts\python.exe app.py
```

Acesse:

**[http://127.0.0.1:5000/site/](http://127.0.0.1:5000/site/)**

Para encerrar, pressione **Ctrl + C** no terminal.

> Essa execução utiliza o servidor de desenvolvimento do Flask. A configuração Docker utiliza Gunicorn.

## 5. Localização do banco

| Ambiente | Localização padrão |
| --- | --- |
| **Python local** | `backend/kredita.db` |
| **Docker** | `/app/data/kredita.db`, no volume `data` |

A variável `DATABASE_URL` permite configurar outro caminho para o arquivo SQLite.

O esquema está em:

[`backend/banco_de_dados/001_sqlite.sql`](../backend/banco_de_dados/001_sqlite.sql)

Para conhecer as tabelas e os relacionamentos, consulte a documentação do [Banco de dados](documentacao-dados/banco_de_dados.md).

## 6. Atualização por fontes públicas

O importador possui rotinas de consulta ao IBGE, BCB e MDS para os indicadores contemplados pela implementação.

Esse processo não coleta novamente todos os indicadores. A cobertura e as regras de reaproveitamento estão descritas no [Fluxo de dados](documentacao-dados/fluxo_de_dados.md).

Os exemplos abaixo utilizam Docker e devem ser executados na raiz do projeto.

> `2026-01` é uma competência de exemplo. Substitua pela competência desejada, respeitando a edição de referência e a disponibilidade das fontes.

### Modo guiado

```powershell
docker compose exec web python importar_kredita.py --guiado
```

Solicita a competência, consulta as fontes, apresenta a prévia e pede confirmação antes da publicação.

### Gerar uma prévia por comando

```powershell
docker compose exec web python importar_kredita.py --atualizar-apis --competencia 2026-01
```

Consulta as fontes e apresenta o resultado da atualização sem publicar uma nova edição.

### Publicar a atualização

Após avaliar a prévia:

```powershell
docker compose exec web python importar_kredita.py --atualizar-apis --competencia 2026-01 --publicar
```

Esse comando executa a atualização e solicita sua publicação no banco. Como realiza uma nova consulta às fontes, os dados retornados podem diferir da prévia anterior.

### Execução sem Docker

Na pasta `backend`, utilize o Python do ambiente virtual com as mesmas opções:

```powershell
..\.venv\Scripts\python.exe importar_kredita.py --guiado
```

### Cuidados de interpretação

- Dados reaproveitados mantêm sua referência original.
- Informações ausentes não recebem automaticamente zero ou nota neutra.
- A indisponibilidade de indicadores necessários pode deixar municípios sem score.
- Uma nova competência não significa que todas as fontes foram atualizadas naquele mês.

O botão **“Atualizar dados”** do site apenas solicita novamente o conteúdo ao backend. Ele não executa essa rotina de coleta e publicação.

## 7. Importação de uma nova base

Também é possível processar uma pasta com uma nova exportação compatível com o projeto.

Os comandos abaixo utilizam a execução local com Python, a partir da pasta `backend`.

Substitua `C:\caminho\nova-edicao` pelo caminho real dos arquivos.

### Validar o pacote

```powershell
..\.venv\Scripts\python.exe importar_kredita.py "C:\caminho\nova-edicao" --validar
```

### Preparar a prévia com recálculo

```powershell
..\.venv\Scripts\python.exe importar_kredita.py "C:\caminho\nova-edicao" --prever-recalculo
```

### Publicar o resultado recalculado

```powershell
..\.venv\Scripts\python.exe importar_kredita.py "C:\caminho\nova-edicao" --publicar-recalculado
```

Esse fluxo verifica a compatibilidade metodológica e aplica as regras de reaproveitamento disponíveis.

Além do `score_kredita.json`, o fluxo de recálculo utiliza `caged_i06_zeros.csv` para classificar os zeros do I06. O arquivo `observacoes_historicas.csv` pode fornecer observações históricas adicionais, quando disponível.

> A pasta precisa conter arquivos no formato esperado pelo importador. Não basta renomear uma planilha ou um JSON de outra estrutura.

## 8. Conteúdo sobre apostas

O arquivo `backend/dados/apostas.json` fornece os estudos e as estimativas utilizados como conteúdo contextual.

Essas informações são armazenadas separadamente dos indicadores do score.

Os dados de apostas não participam do cálculo do score nem do cofator.

## 9. API da aplicação

Os endereços abaixo são relativos ao endereço em que a aplicação está sendo executada.

| Endpoint | Finalidade |
| --- | --- |
| `GET /api/ranking?pagina=1&limite=50&uf=SP&busca=` | Consultar o ranking paginado com filtros. |
| `GET /api/municipios` | Consultar o catálogo e os resultados da edição atual. |
| `GET /api/municipios?simulacao=1` | Incluir os dados da simulação SCR no retorno do catálogo. |
| `GET /api/municipios?simulacao=somente` | Consultar os dados da série simulada. |
| `GET /api/municipios/1100015` | Consultar o resultado e o detalhamento de um município. |
| `GET /api/municipios/1100015?edicao=1` | Consultar o município em uma edição específica existente. |
| `GET /api/municipios/1100015/historico` | Consultar edições publicadas e simulação SCR em séries distintas. |
| `GET /api/apostas` | Consultar o estudo e as estimativas territoriais disponíveis. |
| `GET /api/metodologia` | Consultar o dicionário dos indicadores. |

Os códigos municipais e identificadores de edição apresentados são exemplos e devem ser substituídos conforme a consulta.

## 10. Testes automatizados

Os testes estão em `backend/tests`.

Para executá-los localmente, entre na pasta `backend` e utilize:

```powershell
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O terminal apresenta os testes executados e eventuais falhas.

Na configuração Docker consultada, a pasta de testes não é copiada para a imagem. Por isso, este guia utiliza o ambiente local para executá-los.

## 11. Problemas comuns

<details>
<summary><strong>O Docker não inicia ou o terminal não consegue se conectar</strong></summary>

Abra o Docker Desktop e aguarde sua inicialização.

Se houver uma solicitação de configuração do WSL 2 ou de reinicialização do computador, conclua as etapas indicadas pelo instalador.

Para verificar a conexão:

```powershell
docker info
```

</details>

<details>
<summary><strong>A porta 8788 está ocupada</strong></summary>

No PowerShell, escolha outra porta:

```powershell
$env:KREDITA_HTTP_PORT = "8789"
```

Depois execute:

```powershell
docker compose up -d
```

Acesse `http://127.0.0.1:8789/site/`.

</details>

<details>
<summary><strong>O Docker não encontra o arquivo de configuração</strong></summary>

Execute os comandos na raiz da pasta `KREDITA`, onde está o arquivo `compose.yaml`.

</details>

<details>
<summary><strong>O container encerra ou reinicia continuamente</strong></summary>

Consulte os registros:

```powershell
docker compose logs --tail=100 web
```

Uma falha na importação pode impedir a inicialização do servidor. Registre a mensagem apresentada para análise pela equipe.

</details>

<details>
<summary><strong>A página não abre</strong></summary>

Confira:

- Se o Docker Desktop está em execução.
- Se o serviço aparece em `docker compose ps`.
- Se os registros indicam que o servidor iniciou.
- Se a porta do endereço corresponde à configuração.
- Se o endereço local utiliza `http`.

</details>

<details>
<summary><strong>Uma fonte pública está indisponível</strong></summary>

A atualização depende dos serviços externos e da disponibilidade de dados para a competência solicitada.

Verifique a prévia antes de publicar. A rotina pode reaproveitar observações elegíveis ou manter informações ausentes, conforme as regras implementadas.

Não substitua dados ausentes por zero apenas para concluir a atualização.

</details>

## Documentação relacionada

- [Fluxo de dados](documentacao-dados/fluxo_de_dados.md)
- [Banco de dados](documentacao-dados/banco_de_dados.md)
- [Indicadores](documentacao-dados/indicadores.md)
- [Metodologia do score](documentacao-dados/score.md)
- [Cofator de reajuste](documentacao-dados/cofator.md)