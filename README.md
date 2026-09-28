# Kredita

## Descrição do Desafio
Conceder crédito para populações historicamente recusadas por grandes instituições financeiras exige ir além da visão tradicional de risco: **exige identificar onde residem o consumo reprimido e a capacidade real de pagamento sustentável.**
Neste projeto, nosso objetivo é explorar e transformar dados econômicos públicos do **Banco Central do Brasil (BCB)** em inteligência territorial para apoiar decisões de crédito mais inclusivas e responsáveis.

---

# Product Backlog

| ID | Sprint | Prioridade | User Story | Critérios de Aceite (Definition Of Done) | Est. |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **US01** | 1 | Alta | **Como analista de crédito**, gostaria de coletar dados do BCB (inadimplência, ticket, etc.) e integrar bases de dados públicos, para que a análise reflita o real comprometimento financeiro da região. | - Acesso direto via Colab.<br>- Quebra de faixas de atraso (curta e longa).<br>- Integração de fontes sobre apostas (Bets). | 8 |
| **US02** | 1 | Alta | **Como analista de dados**, gostaria que os indicadores estivessem padronizados e limpos, diferenciando dívida saudável de crítica, para garantir a confiabilidade dos cálculos do Score. | - Limpar dados nulos e valores absurdos (infinitos).<br>- Converter valores monetários de vírgula para ponto.<br>- Classificar dívida imobiliária (saudável) vs. consumo/Bets (crítica). | 8 |
| **US03** | 1 | Alta | **Como usuário final**, desejo visualizar os dados reais processados por meio de gráficos, para facilitar a análise e a compreensão rápida das informações. | - Pelo menos um gráfico gerado plotando dados reais dentro do notebook do Colab. | 3 |
| **US04** | 1 | Alta | **Como usuário**, desejo acessar a estrutura inicial do site web, mesmo sem os dados reais conectados, para visualizar a futura organização do sistema. | - Esqueleto (Site inicial) criado em HTML5/CSS3.<br>- Código salvo e versionado no GitHub. | 3 |
| **US05** | 2 | Alta | **Como tomador de decisões**, gostaria de obter um Score de Oportunidade que valorize a "inadimplência de recuperação rápida" (< 20 dias) e penalize o endividamento crítico, para identificar a real capacidade de pagamento sustentável. | - Fórmula no Colab.<br>- Considerar Fatores: Potencial de Mercado, Dinâmica, Risco Relativo e Saturação.<br>- Identificar histórico de baixa conversão para inadimplência longa (>90 dias). | 13 |
| **US06** | 2 | Alta | **Como desenvolvedor**, desejo que o site consuma os dados limpos através de uma API (1º DSM) em Flask, para automatizar a visualização dos dados reais na web. | - API REST em Flask conectada e retornando os dados do projeto no backend. | 8 |
| **US07** | 2 | Alta | **Como analista de crédito**, gostaria de visualizar um potencial de mercado e uma tabela de ranking regional, para focar investimentos nas melhores áreas. | - Mapa integrado à interface web exibindo o Score.<br>- Tabela classificatória (Ranking) baseada no Score. | 5 |
| **US08** | 2 | Média | **Como analista**, quero poder filtrar os indicadores por cenários e granularidade (Macro/Micro), para analisar dados de forma mais específica e granular. | - Filtros funcionais aplicados no mapa e na tabela do sistema web. | 3 |
| **US09** | 3 | Média | **Como estrategista**, quero comparar detalhadamente duas regiões lado a lado, para decidir com maior precisão qual mercado focar. | - Tela de comparação regional com gráficos paralelos implementada. | 3 |
| **US10** | 3 | Baixa | **Como gestor**, desejo exportar os dados do sistema em formatos variados (PDF, CSV, XLSX, XML), para facilitar apresentações e uso offline. | - Botão de exportação/download na interface gerando os arquivos de maneira válida. | 3 |
| **US11** | 3 | Baixa | **Como cliente**, desejo acessar o website institucional, a metodologia e manuais do sistema, para compreender facilmente a origem do Score e como usar a ferramenta. | - Página pública de documentação, manuais de uso e explicação metodológica online. | 8 |

---

## Sprints e Entregas

| Período da Sprint | Documentação da Sprint | Vídeo do Incremento (YouTube) |
| --- | --- | --- |
| 07/09/2026 - 27/09/2026 | [Documentação Sprint 1](https://www.google.com/search?q=link-para-doc) | [Assistir no YouTube](https://www.google.com/search?q=link-para-video) |
| 05/10/2026 - 25/10/2026 | [Documentação Sprint 2](https://www.google.com/search?q=link-para-doc) | [Assistir no YouTube](https://www.google.com/search?q=link-para-video) |
| 02/11/2026 - 22/11/2026 | [Documentação Sprint 3](https://www.google.com/search?q=link-para-doc) | [Assistir no YouTube](https://www.google.com/search?q=link-para-video) |

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
| Karam Diniz Coutinho |  Product Owner | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/karam-diniz) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](www.linkedin.com/in/karam-diniz) |
| Davi Ribeiro André  | Scrum Master | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DaviRibeiroAndre) |[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davi-ribeiro-andr%C3%A9-a3729b1b3/) |
| Gabriel Herzer Gaspary | Scrum Team | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GabrielHerzer) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-herzer-133220352/) |
| Gabriel Tase Telmo |  Scrum Team | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/gabrieltase) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabriel-tase-telmo-1630a4431/) |
| Igor Makoto Hoshino |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/igormakoto) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/igor-makoto-57198b270/) ||
| Isadora de Sousa Fanti |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/zzadoraa) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/isadora-fanti-543262286/) |
| Júlio Ferreira Siqueira dos Santos |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JulioFSSantos4645) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/julio-ferreira-344a09434/) |
| Pedro Aurélio Freitas Lemos dos Santos Lira |  Scrum Team  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/eoPedroAurelio) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/pedro-aurelio/) |
