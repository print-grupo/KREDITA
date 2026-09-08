# Backlog da Sprint 1

| **ID** | **Sprint** | **Prioridade** | **User Story** | **Critérios de Aceite** |
|--------|------------|----------------|----------------|-------------------------|
| **US01** | 1 | Alta | **Como analista de crédito**, gostaria de coletar dados do BCB, como inadimplência e ticket, e integrar bases de dados públicos, para que a análise reflita o real comprometimento financeiro da região. | - Acesso direto aos dados por meio do Google Colab.<br>- Quebra das faixas de atraso em curta e longa duração.<br>- Integração de fontes públicas sobre apostas esportivas (Bets). |
| **US02** | 1 | Alta | **Como analista de dados**, gostaria que os indicadores estivessem padronizados e limpos, diferenciando dívida saudável de dívida crítica, para garantir a confiabilidade dos dados utilizados no projeto. | - Limpeza de dados nulos e valores absurdos ou infinitos.<br>- Conversão de valores monetários de vírgula para ponto.<br>- Classificação da dívida imobiliária como saudável e da dívida de consumo ou Bets como crítica. |
| **US03** | 1 | Alta | **Como usuário final**, desejo visualizar os dados reais processados por meio de gráficos, para facilitar a análise e a compreensão rápida das informações. | - Pelo menos um gráfico gerado com dados reais dentro do notebook do Google Colab.<br>- Comparação visual entre dívida saudável e dívida crítica.<br>- Visualização das taxas de inadimplência de recuperação rápida e longa. |
| **US04** | 1 | Alta | **Como usuário**, desejo acessar a estrutura inicial do site web, mesmo sem os dados reais conectados, para visualizar a futura organização do sistema. | - Esqueleto inicial do site criado utilizando HTML5 e CSS3.<br>- Estrutura inicial versionada no GitHub.<br>- Código organizado para receber futuras integrações com os dados processados. |

---

## Tasks

| **ID** | **Descrição** |
|--------|---------------|
| **US01-T01** | Criar e compartilhar o notebook base no Google Colab entre os integrantes da equipe. |
| **US01-T02** | Mapear as URLs públicas e a documentação das APIs e fontes do BCB, IBGE, Data Senado e SPA. |
| **US01-T03** | Desenvolver um script Python, utilizando `requests` ou `pandas`, para importar os dados crus do BCB relacionados à inadimplência e ao ticket. |
| **US01-T04** | Desenvolver um script Python para extrair dados sobre apostas esportivas (Bets) das demais fontes públicas selecionadas. |
| **US02-T01** | Desenvolver uma rotina com Pandas para identificar e remover linhas nulas (`NaN`) e valores infinitos. |
| **US02-T02** | Criar uma função Python para substituir vírgulas por pontos e converter as colunas financeiras para o tipo `float`. |
| **US02-T03** | Criar uma nova coluna no DataFrame para classificar os dados como “Saudável” ou “Crítica”. |
| **US03-T01** | Importar as bibliotecas Matplotlib e Seaborn no notebook do Google Colab. |
| **US03-T02** | Desenvolver um gráfico de barras comparando o volume total de dívida saudável e dívida crítica nas regiões. |
| **US03-T03** | Desenvolver um gráfico comparando a taxa de inadimplência de recuperação rápida, inferior a vinte dias, com a inadimplência longa, superior a noventa dias. |
| **US04-T01** | Configurar o repositório do GitHub para o frontend e definir um padrão inicial de commits. |
| **US04-T02** | Desenvolver o arquivo `index.html` utilizando uma estrutura semântica HTML5. |
| **US04-T03** | Criar o arquivo `style.css` com a marcação visual, o layout e a responsividade utilizando CSS3. |
| **US04-T04** | Realizar o primeiro push do código para a branch principal do projeto, como `main` ou `develop`. |

---

## Campos a serem definidos posteriormente

Os seguintes campos serão adicionados ou preenchidos posteriormente, quando a equipe definir os critérios:

- Definition of Ready (DoR)
- Definition of Done (DoD)
- Estimativa das User Stories
- Estimativa das Tasks
