# Indicadores Econômicos e Sociais

Este documento apresenta os indicadores selecionados para o projeto,
os dados necessários para sua obtenção, as fontes utilizadas,e as limitações identificadas.

Os indicadores estão organizados em eixos temáticos relacionados
à análise de risco, capacidade financeira, inclusão financeira e
características demográficas das regiões analisadas. 

# Indicadores

## Eixo 1 — Risco de Crédito

### 1. Inadimplência por Estado

**O que queremos descobrir:**

Qual é a proporção da carteira de crédito da região que está inadimplente?

**Dados necessários:**

- Carteira de crédito ativa
- Carteira inadimplente
- UF
- Período

**Fonte:** Banco Central do Brasil — SCR.data

**Link:** https://dadosabertos.bcb.gov.br/dataset/scr_data

**Endpoint:** Disponibilizado por arquivos mensais do SCR.data; não há um endpoint REST público simples para consulta direta dos dados.

---

### 2. Fragilidade de Renda

**O que queremos descobrir:**

Quanto a população de determinada região está exposta a baixa renda, o que pode indicar menor capacidade de absorver uma dívida?

**Dados necessários:**

- Renda domiciliar per capita
- População por faixa de renda
- Proporção da população em baixa renda
- UF
- Período

**Fonte:** IBGE — SIDRA / PNAD Contínua

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/7127/n3/all

---

### 3. Persistência >90 dias

**O que queremos descobrir:**

Entre os créditos inadimplentes, qual parcela apresenta atraso superior a 90 dias?

**Dados necessários:**

- Carteira inadimplente
- Valores vencidos acima de 90 dias
- UF
- Período

**Fonte:** Banco Central do Brasil — SCR.data

**Link:** https://dadosabertos.bcb.gov.br/dataset/scr_data

**Endpoint:** Disponibilizado por arquivos mensais do SCR.data; não há um endpoint REST público simples para consulta direta dos dados.

---

# Eixo 2 — Capacidade Financeira

### 4. Emprego/Desemprego

**O que queremos descobrir:**

Qual parcela da população economicamente ativa está ocupada ou desocupada?

**Dados necessários:**

- Pessoas ocupadas
- Pessoas desocupadas
- População na força de trabalho
- UF / Município
- Período

**Fonte:** IBGE — PNAD Contínua / SIDRA

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/4093/n3/all

---

### 5. Remuneração Média

**O que queremos descobrir:**

Quanto os trabalhadores recebem em média, indicando a capacidade econômica do mercado de trabalho?

**Dados necessários:**

- Remuneração média
- Trabalhadores ocupados
- UF / Município
- Período

**Fonte:** Ministério do Trabalho e Emprego — RAIS / CAGED

**Link:** https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged

**Endpoint:** Não identificado como API REST pública. Os dados são disponibilizados principalmente por arquivos/microdados.

---

### 6. Dinamismo do Mercado de Trabalho

**O que queremos descobrir:**

Se a região está criando ou perdendo empregos formais.

**Dados necessários:**

- Admissões
- Desligamentos
- Município
- UF
- Período

**Fonte:** Ministério do Trabalho e Emprego — CAGED

**Link:** https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged

**Endpoint:** Não identificado como API REST pública. Utilização prevista por meio dos microdados do CAGED.

---

### 7. Renda per Capita

**O que queremos descobrir:**

Quanto, em média, cada pessoa possui de renda domiciliar na região?

**Dados necessários:**

- Renda domiciliar per capita
- UF / Município
- Período

**Fonte:** IBGE — SIDRA / PNAD Contínua

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/7127/n3/all

---

### 8. Empréstimos/Depósitos

**O que queremos descobrir:**

Quanto o sistema financeiro local empresta em relação aos depósitos captados?

**Dados necessários:**

- Empréstimos
- Depósitos
- Região
- Período

**Fonte:** Banco Central do Brasil

**Link:** https://dadosabertos.bcb.gov.br/

**Endpoint:** 

---

# Eixo 3 — Inclusão Financeira

### 9. CadÚnico / Bolsa Família

**O que queremos descobrir:**

Qual proporção da população está cadastrada ou é beneficiária de programas de assistência social?

**Dados necessários:**

- Famílias cadastradas no CadÚnico
- Pessoas cadastradas
- Beneficiários do Bolsa Família
- População
- Município / UF
- Período

**Fonte:** Ministério do Desenvolvimento e Assistência Social — CadÚnico

**Link:** https://www.gov.br/conecta/catalogo/apis/cadunico-servicos-indicadores-familiares

**Endpoint:** https://apigateway.conectagov.estaleiro.serpro.gov.br/api-cadunico-servicos-indicadores/v1/dp/indicadoresFamiliar/{cpf}

**Observação:** A API exige CPF/NIS para consulta individual e autenticação/integração com a plataforma Conecta gov.br. Não deve ser tratada automaticamente como uma API pública para obter agregados municipais. :contentReference[oaicite:1]{index=1}

---

### 10. Crédito per Capita

**O que queremos descobrir:**

Quanto de crédito existe, em média, para cada habitante da região?

**Dados necessários:**

- Carteira de crédito
- População
- UF / Município
- Período

**Fonte:** Banco Central do Brasil — SCR.data / IBGE

**Link:** https://dadosabertos.bcb.gov.br/dataset/scr_data

**Endpoint:** SCR.data — arquivos mensais; população via API SIDRA.

**Endpoint IBGE:** https://apisidra.ibge.gov.br/values/t/4714/n3/all

---

### 11. Informalidade

**O que queremos descobrir:**

Qual proporção dos trabalhadores está na informalidade?

**Dados necessários:**

- População ocupada
- Trabalhadores em situação de informalidade
- UF / Município
- Período

**Fonte:** IBGE — PNAD Contínua / SIDRA

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/4093/n3/all

---

# Eixo 4 — Demografia

### 12. Crescimento Populacional

**O que queremos descobrir:**

Se a região está crescendo, indicando expansão do mercado local.

**Dados necessários:**

- População residente
- Região
- Período

**Fonte:** IBGE — SIDRA

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/6579/n3/all

---

### 13. % PEA

**O que queremos descobrir:**

Qual é o tamanho da força de trabalho em relação à população da região?

**Dados necessários:**

- População economicamente ativa
- População total
- UF / Município
- Período

**Fonte:** IBGE — PNAD Contínua / SIDRA

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/4093/n3/all

---

### 14. População Absoluta

**O que queremos descobrir:**

Qual é o tamanho do mercado consumidor potencial?

**Dados necessários:**

- População residente
- UF / Município
- Período

**Fonte:** IBGE — SIDRA / Censo Demográfico

**Link:** https://sidra.ibge.gov.br/

**Endpoint:** https://apisidra.ibge.gov.br/values/t/4709/n3/all

---

### 15. Agências Bancárias

**O que queremos descobrir:**

Quanto acesso físico ao sistema bancário existe na região?

**Dados necessários:**

- Número de agências bancárias
- Município
- UF
- Período

**Fonte:** Banco Central do Brasil — Agências de Instituições Supervisionadas

**Link:** https://dadosabertos.bcb.gov.br/dataset/agencias-de-instituicoes-supervisionadas-pelo-bacen

**Endpoint:** Disponível por API/OData do Portal de Dados Abertos do BCB.

---

### 16. Estrutura Etária

**O que queremos descobrir:**

Qual é a composição da população por faixa etária?

**Dados necessários:**

- População jovem
- População em idade de trabalho
- População idosa
- Município / UF
- Período

**Fonte:** IBGE — Censo Demográfico 2022 / SIDRA

**Link:** https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html

**Endpoint:** https://apisidra.ibge.gov.br/values/t/9514/n3/all
