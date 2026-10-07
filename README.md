# Kredita

## Descrição do Desafio
Conceder crédito para populações historicamente recusadas por grandes instituições financeiras exige ir além da visão tradicional de risco: **exige identificar onde residem o consumo reprimido e a capacidade real de pagamento sustentável.**
Neste projeto, nosso objetivo é explorar e transformar dados econômicos públicos do **Banco Central do Brasil (BCB)** em inteligência territorial para apoiar decisões de crédito mais inclusivas e responsáveis.

---

# Product Backlog

| ID | Sprint | Prioridade | User Story | Critérios de Aceite | Est. |
|---|---|---|---|---|---|
| **US01** | 1 | Alta | **Como analista de crédito**, gostaria de coletar os dados necessários aos indicadores definidos no projeto e integrar diferentes fontes públicas, para que a análise represente as características financeiras, sociais e demográficas das regiões analisadas. | - Fontes e formas de acesso aos dados dos indicadores identificadas e documentadas.<br>- Dados coletados e disponibilizados no Google Colab.<br>- Dados organizados com identificação da região e do período de referência, conforme a disponibilidade das fontes.<br>- Limitações e indisponibilidades encontradas na coleta registradas. | **8** |
| **US02** | 1 | Alta | **Como analista de dados**, gostaria que os dados coletados para os indicadores estivessem limpos, padronizados e organizados, para garantir a confiabilidade das informações utilizadas nas análises do projeto. | - Dados nulos, infinitos e inconsistentes identificados e tratados conforme os critérios definidos pela equipe.<br>- Tipos de dados e formatos numéricos padronizados conforme as necessidades de cada base.<br>- Dados organizados em arquivos ou DataFrames no Google Colab.<br>- Bases preparadas para a construção dos gráficos e as próximas etapas de análise. | **8** |
| **US03** | 1 | Alta | **Como usuário final**, desejo visualizar os dados reais processados por meio de gráficos dos diferentes eixos do projeto, para facilitar a análise e a compreensão das características das regiões. | - Gráficos desenvolvidos com dados reais dos Eixos 1 e 2: Risco de Crédito e Capacidade Financeira.<br>- Gráficos desenvolvidos com dados reais dos Eixos 3 e 4: Inclusão Financeira e Demografia.<br>- Indicadores, regiões, períodos e unidades identificados nas visualizações, quando aplicáveis.<br>- Gráficos integrados ao site e apresentados de forma legível. | **3** |
| **US04** | 1 | Alta | **Como usuário**, desejo acessar a primeira versão do site do projeto, com páginas e elementos organizados, para conhecer a proposta da ferramenta e visualizar as informações iniciais disponíveis. | - Primeira versão do site desenvolvida com HTML5 e CSS3.<br>- Páginas, navegação e elementos visuais implementados conforme a proposta definida pela equipe.<br>- Estrutura, layout e responsividade revisados, com correções e melhorias aplicadas.<br>- Código organizado para futuras integrações com o backend.<br>- Código versionado no GitHub conforme os padrões de branches e commits definidos pela equipe. | **3** |
| **US05** | 2 | Alta | **Como tomador de decisões**, gostaria de obter um Score baseado nos indicadores definidos no projeto, considerando suas relações, pesos e características, para apoiar a análise das condições financeiras e do risco das regiões. | - Indicadores utilizados no Score definidos e revisados.<br>- Relações entre os indicadores analisadas.<br>- Pesos dos indicadores definidos.<br>- Níveis estadual e municipal identificados.<br>- Relação entre indicadores estaduais e municipais definida.<br>- Método de cálculo do Score definido no Google Colab.<br>- Critérios utilizados para o Score documentados. | **13** |
| **US06** | 2 | Alta | **Como analista de dados**, gostaria de organizar e otimizar o processo de tratamento e extração das informações e utilizá-las na construção de um ranking regional, para facilitar a análise e comparação entre as regiões do projeto. | - Decisões sobre os indicadores registradas no Google Colab.<br>- Estrutura para relacionar indicadores estaduais e municipais definida no Colab.<br>- Processo de extração analisado e otimizado.<br>- Desempenho do Colab melhorado.<br>- Método para construção do ranking regional definido.<br>- Ranking regional estruturado a partir dos dados do projeto. | **8** |
| **US07** | 2 | Alta | **Como tomador de decisões**, gostaria de analisar a evolução histórica do Score e identificar o potencial econômico das regiões, para compreender o comportamento dos resultados ao longo do tempo e apoiar a identificação das regiões com maior potencial. | - Histórico do Score disponível.<br>- Gráficos de linha representando a evolução dos resultados.<br>- Evolução do Score analisada ao longo do tempo.<br>- Método para identificar o potencial econômico regional definido com base no histórico.<br>- Documentação do GitHub atualizada com as decisões e resultados da Sprint. | **8** |
| **US08** | 2 | Alta | **Como usuário**, gostaria de acessar uma aplicação web com frontend e backend integrados, para visualizar e utilizar as funcionalidades e informações desenvolvidas pelo projeto. | - Funcionalidades e estrutura da aplicação definidas.<br>- Páginas, elementos e organização visual especificados.<br>- Frontend desenvolvido conforme as definições estabelecidas.<br>- Backend desenvolvido para atender às funcionalidades da aplicação.<br>- Integração entre frontend e backend realizada.<br>- Aplicação preparada para receber e apresentar os dados do projeto. | **13** |
| **US09** | 3 | Média | **Como estrategista**, quero comparar detalhadamente duas regiões lado a lado, para decidir com maior precisão qual mercado focar. | - Tela de comparação regional implementada.<br>- Exibição de duas regiões selecionadas lado a lado.<br>- Gráficos paralelos para facilitar a comparação dos indicadores. | **3** |
| **US10** | 3 | Baixa | **Como gestor**, desejo exportar os dados do sistema em formatos variados, como PDF, CSV, XLSX e XML, para facilitar apresentações e o uso offline. | - Botão de exportação ou download disponível na interface.<br>- Geração dos arquivos nos formatos PDF, CSV, XLSX e XML.<br>- Arquivos exportados gerados de maneira válida. | **3** |
| **US11** | 3 | Baixa | **Como cliente**, desejo acessar o website institucional, a metodologia e os manuais do sistema, para compreender facilmente a origem do Score e como utilizar a ferramenta. | - Página pública de documentação implementada.<br>- Disponibilização dos manuais de uso do sistema.<br>- Explicação da metodologia utilizada no desenvolvimento do Score. | **8** |
| **US12** | 3 | Média | **Como analista**, quero filtrar os indicadores por cenários e níveis geográficos disponíveis, para analisar as informações de forma mais específica e comparar os resultados conforme o recorte selecionado. | - Filtros de cenário e nível geográfico disponíveis na interface, conforme os dados do projeto.<br>- Filtros aplicados ao mapa e à tabela de ranking.<br>- Informações exibidas atualizadas conforme os filtros selecionados.<br>- Ausência de dados para o recorte selecionado informada ao usuário. | **5** |
---

## Sprints e Entregas

| Período da Sprint | Documentação da Sprint | Vídeo do Incremento (YouTube) |
| --- | --- | --- |
| 07/09/2026 - 27/09/2026 | [![Sprint 1](https://img.shields.io/badge/Sprint%201-Documenta%C3%A7%C3%A3o-36a2eb?style=flat&logo=markdown&logoColor=white)](./docs/scrum/backlog/sprint-1.md) | [![YouTube](https://img.shields.io/badge/YouTube-Assista%20ao%20v%C3%ADdeo-FF0000?style=flat&logo=youtube&logoColor=white)](https://youtu.be/ADqZf03HH-4) |
| 05/10/2026 - 25/10/2026 | [![Sprint 2](https://img.shields.io/badge/Sprint%202-Documenta%C3%A7%C3%A3o-36a2eb?style=flat&logo=markdown&logoColor=white)](./docs/scrum/backlog/sprint-2.md) | [Assistir no YouTube](https://www.google.com/search?q=link-para-video) |
| 02/11/2026 - 22/11/2026 | [![Sprint 3](https://img.shields.io/badge/Sprint%203-Documenta%C3%A7%C3%A3o-36a2eb?style=flat&logo=markdown&logoColor=white)](./docs/scrum/backlog/sprint-3.md) | [Assistir no YouTube](https://www.google.com/search?q=link-para-video) |

---

## 🧰 ferramentas utilizadas 

### Interface Web

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)

### Desenvolvimento

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

### Tratamento e Análise de Dados

![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=flat&logo=googlecolab&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/14L3S4EmFeAGcKZXWWj69y9KhEUn5McOE?usp=sharing)

### Organização do Projeto

![Lefthook](https://img.shields.io/badge/Lefthook-000000?style=flat)
![Jira](https://img.shields.io/badge/Jira-0052CC?style=flat&logo=jira&logoColor=white)

## ✅ Critérios de Prontidão (DoR) e Conclusão (DoD)

### 📋 Definição de Pronto — DoR

Uma tarefa ou User Story estará pronta para desenvolvimento quando:

- A descrição estiver definida e compreendida pela equipe.
- Os critérios de aceite estiverem estabelecidos.
- As informações e dependências necessárias estiverem identificadas.
- A estimativa da tarefa estiver definida pela equipe.

### 🏁 Definição de Feito — DoD

Uma tarefa ou User Story será considerada concluída quando:

- O desenvolvimento previsto tiver sido realizado.
- Os critérios de aceite tiverem sido atendidos.
- O resultado tiver sido revisado por outro integrante da equipe.
- As alterações estiverem versionadas no GitHub.
- A documentação relacionada tiver sido atualizada quando necessário.

### 📌 DoR e DoD por Sprint

#### Sprint 1 — Coleta, Tratamento, Visualização e Site Inicial

**DoR:**
- User Stories da Sprint validadas pela equipe.
- Indicadores e fontes de dados definidos.
- Estrutura do Google Colab disponível para desenvolvimento.
- Ambiente de desenvolvimento preparado.

**DoD:**
- Dados iniciais dos indicadores coletados e disponibilizados no Colab.
- Dados tratados e preparados para análise.
- Gráficos dos eixos definidos desenvolvidos.
- Estrutura inicial do site implementada e revisada.
- Alterações versionadas no GitHub.

#### Sprint 2 — Score e Integração

**DoR:**

**DoD:**


#### Sprint 3 — Comparação, Exportação e Documentação

**DoR:**

**DoD:**


---

## Estratégia de Branch

* `main`: Versão estável, testada e pronta para produção.
* `develop`: Branch de integração para o desenvolvimento contínuo e união das features.
* `feature/nome-da-feature`: Branches criadas a partir da `develop` para o desenvolvimento de novas funcionalidades.
* `fix/nome-do-bug`: Branches criadas para a correção de bugs pontuais.

---

## Manual de Usuário

[ preencher ]

---

## Equipe

| Nome Completo | Papel | GitHub | LinkedIn |
| --- | --- | --- | --- |
| Gabriel Herzer Gaspary | Product Owner | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GabrielHerzer) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-herzer-133220352/) |
| Davi Ribeiro André | Scrum Master | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DaviRibeiroAndre) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davi-ribeiro-andr%C3%A9-a3729b1b3/) |
| Karam Diniz Coutinho | Scrum Team | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/karam-diniz) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/karam-diniz) |
| Gabriel Tase Telmo |  Scrum Team | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/gabrieltase) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-tase-telmo-1630a4431/) |
| Igor Makoto Hoshino |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/igormakoto) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/igor-makoto-57198b270/) ||
| Isadora de Sousa Fanti |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/zzadoraa) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/isadora-fanti-543262286/) |
| Júlio Ferreira Siqueira dos Santos |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JulioFSSantos4645) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/julio-ferreira-344a09434/) |
| Pedro Aurélio Freitas Lemos dos Santos Lira |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/eoPedroAurelio) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/pedro-aurelio/) |
