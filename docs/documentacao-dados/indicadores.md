# Indicadores Econômicos e Sociais

Este documento apresenta os indicadores selecionados para o KREDITA, as perguntas que orientam sua utilização, os dados necessários, as fontes e as limitações de interpretação.

Os indicadores estão organizados em quatro eixos:

- **Eixo 1 — Risco**
- **Eixo 2 — Capacidade financeira e atividade**
- **Eixo 3 — Inclusão**
- **Eixo 4 — Demografia e infraestrutura**

A organização contempla **16 itens: 15 indicadores utilizados no Score e a população absoluta como informação complementar**, sem nota ou peso próprio.

As fórmulas de normalização e os pesos estão disponíveis na [Metodologia do Score](./score.md).

## Níveis geográficos e referências

Os indicadores **I01, I03, I08 e I11** utilizam valores estaduais na base adotada pelo projeto. A aplicação do cofator produz uma **estimativa municipal experimental**, não um dado municipal observado ou publicado pela fonte.

O funcionamento desse ajuste está documentado em [Cofator de reajuste](./cofator.md).

Os demais indicadores utilizam dados municipais. Cada fonte possui sua própria referência temporal: dados do Censo, estimativas anuais e registros mensais não devem ser apresentados como se tivessem sido coletados no mesmo período.

Dados ausentes devem ser identificados como indisponíveis, sem substituição automática por zero.

---

## Eixo 1 — Risco

### I01 · Inadimplência PF

**O que queremos descobrir:**

Qual proporção da carteira ativa de crédito de pessoas físicas está associada a operações inadimplentes?

**Dados necessários:**

- Carteira ativa de crédito de pessoas físicas.
- Carteira inadimplente de pessoas físicas.
- UF.
- Período de referência.

**Medida utilizada:** carteira inadimplente PF em relação à carteira ativa PF, em percentual.

**Nível geográfico:** estadual, com estimativa municipal experimental pelo cofator.

**Fonte:** Banco Central do Brasil — SCR.data.

**Link:** [SCR.data — Banco Central](https://dadosabertos.bcb.gov.br/dataset/scr_data)

**Forma de obtenção:** arquivos do SCR.data, selecionando o período, a UF e o recorte de pessoas físicas.

**Limitações:**

A taxa estadual não representa diretamente a inadimplência de cada município. O ajuste pelo cofator diferencia as estimativas conforme os critérios do projeto, mas não substitui uma medição municipal.

A carteira inadimplente não deve ser confundida com o saldo das parcelas vencidas utilizado no I03.

### I02 · Fragilidade de renda

**O que queremos descobrir:**

Qual parcela da população vive em domicílios com renda per capita de até meio salário mínimo?

**Dados necessários:**

- Pessoas em domicílios com renda per capita de até meio salário mínimo.
- Total de pessoas no universo correspondente da tabela.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** percentual de pessoas na faixa de renda definida.

**Nível geográfico:** municipal.

**Fonte:** IBGE — Censo Demográfico 2022, SIDRA, tabela 10296.

**Link:** [SIDRA — Tabela 10296](https://sidra.ibge.gov.br/tabela/10296)

**Forma de obtenção:** consulta à tabela no SIDRA, com seleção das faixas de renda e do recorte municipal.

**Limitações:**

O indicador retrata as condições registradas no Censo 2022. Não representa uma atualização mensal da renda municipal nem equivale à proporção de pessoas cadastradas no CadÚnico.

### I03 · Composição dos saldos vencidos 90+

**O que queremos descobrir:**

Entre os saldos vencidos considerados no cálculo, qual parcela corresponde a atrasos superiores a 90 dias?

**Dados necessários:**

- Saldo vencido de 15 a 90 dias.
- Saldo vencido acima de 90 dias.
- Recorte de pessoas físicas.
- UF.
- Período de referência.

**Medida utilizada:** saldo vencido acima de 90 dias dividido pela soma dos saldos vencidos de 15 a 90 dias e acima de 90 dias, em percentual.

**Nível geográfico:** estadual, com estimativa municipal experimental pelo cofator.

**Fonte:** Banco Central do Brasil — SCR.data.

**Link:** [SCR.data — Banco Central](https://dadosabertos.bcb.gov.br/dataset/scr_data)

**Forma de obtenção:** arquivos do SCR.data, selecionando os campos de saldos vencidos e o recorte de pessoas físicas.

**Limitações:**

O indicador descreve a composição dos atrasos no período. Não acompanha a permanência de uma mesma dívida ao longo do tempo e, por isso, não é denominado “persistência”.

Seu denominador é diferente do utilizado no I01.

---

## Eixo 2 — Capacidade financeira e atividade

### I04 · Desocupação de pessoas de 14 anos ou mais

**O que queremos descobrir:**

Qual parcela da força de trabalho de 14 anos ou mais está desocupada?

**Dados necessários:**

- Pessoas desocupadas de 14 anos ou mais.
- Pessoas na força de trabalho de 14 anos ou mais.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** pessoas desocupadas em relação à força de trabalho, em percentual.

**Nível geográfico:** municipal.

**Fonte:** IBGE — Censo Demográfico 2022, SIDRA, tabela 9517.

**Link:** [SIDRA — Tabela 9517](https://sidra.ibge.gov.br/tabela/9517)

**Forma de obtenção:** consulta municipal à tabela, selecionando as categorias de condição em relação à força de trabalho.

**Limitações:**

Pessoas fora da força de trabalho não são contabilizadas como desocupadas. Uma taxa baixa de desocupação, isoladamente, não demonstra alta participação econômica da população.

A referência utilizada é o Censo 2022.

### I05 · Salário médio de admissão mensal

**O que queremos descobrir:**

Qual é o salário médio informado nas novas contratações formais do município?

**Dados necessários:**

- Registros de admissões.
- Salários válidos com periodicidade mensal.
- Município e código de identificação.
- Mês e ano de referência.

**Medida utilizada:** média dos salários mensais válidos das admissões selecionadas, em reais.

**Nível geográfico:** municipal.

**Fonte:** Ministério do Trabalho e Emprego — Novo CAGED.

**Link:** [Microdados RAIS e CAGED](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged)

**Forma de obtenção:** arquivos de movimentações do Novo CAGED, filtrando admissões e salários mensais válidos.

**Limitações:**

O indicador representa os salários das novas contratações, não a remuneração média de todos os trabalhadores.

Poucas admissões podem tornar a média sensível a contratações específicas. Sem admissões com salário válido, o indicador fica indisponível.

### I06 · Saldo formal por mil habitantes

**O que queremos descobrir:**

O município está criando ou perdendo vínculos formais de trabalho, proporcionalmente à sua população?

**Dados necessários:**

- Quantidade de admissões.
- Quantidade de desligamentos.
- População municipal.
- Município e código IBGE.
- Mês das movimentações e ano da população utilizada.

**Medida utilizada:** admissões menos desligamentos, divididos pela população e multiplicados por mil.

**Nível geográfico:** municipal.

**Fontes:**

- Ministério do Trabalho e Emprego — Novo CAGED.
- IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Links:**

- [Microdados RAIS e CAGED](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged)
- [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** agregação municipal das movimentações do CAGED e associação com a população pelo código do município.

**Limitações:**

O saldo mede movimentações de vínculos formais, não a quantidade de pessoas empregadas. Resultados mensais podem refletir sazonalidade e não representam o mercado informal.

### I07 · Renda domiciliar per capita

**O que queremos descobrir:**

Qual é o rendimento domiciliar médio por pessoa no município?

**Dados necessários:**

- Rendimento nominal médio mensal domiciliar per capita.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** rendimento domiciliar per capita publicado pelo IBGE, em reais.

**Nível geográfico:** municipal.

**Fonte:** IBGE — Censo Demográfico 2022, SIDRA, tabela 10295.

**Link:** [SIDRA — Tabela 10295](https://sidra.ibge.gov.br/tabela/10295)

**Forma de obtenção:** consulta municipal à variável de rendimento domiciliar per capita no SIDRA.

**Limitações:**

A média não descreve a distribuição da renda entre os moradores. Os valores utilizados são nominais de 2022 e não devem ser apresentados como renda atualizada para o período dos indicadores mensais.

### I08 · Relação crédito/depósitos

**O que queremos descobrir:**

Qual é a relação entre o volume de crédito e os depósitos bancários registrados na UF?

**Dados necessários:**

- Volume de crédito.
- Volume de depósitos nas rubricas selecionadas.
- UF.
- Período de referência.

**Medida utilizada:** crédito dividido pelos depósitos considerados na extração.

Na versão utilizada pelo projeto, o crédito corresponde ao verbete **160** e os depósitos à soma dos verbetes **401, 420 e 432**.

**Nível geográfico:** estadual na extração adotada, com estimativa municipal experimental pelo cofator.

**Fonte:** Banco Central do Brasil — Estatística Bancária Mensal por Município, ESTBAN.

**Link:** [ESTBAN — Banco Central](https://www.bcb.gov.br/estatisticas/estatisticabancariamunicipios)

**Forma de obtenção:** arquivos do ESTBAN, com seleção das rubricas e agregação dos valores por UF.

**Limitações:**

Embora a fonte disponibilize informações por município, a versão atual do projeto utiliza valores agregados por UF.

A relação não representa diretamente a capacidade de pagamento dos moradores nem deve ser interpretada como medida prudencial de liquidez bancária.

### I09 · Volume Pix pago por PF por habitante

**O que queremos descobrir:**

Qual é o volume de pagamentos Pix realizados por pessoas físicas em relação à população do município?

**Dados necessários:**

- Valor mensal de Pix pago por pessoas físicas.
- População municipal.
- Município e código de identificação.
- Mês dos pagamentos e ano da população utilizada.

**Medida utilizada:** valor mensal de Pix pago por PF dividido pela população municipal.

**Unidade:** reais por habitante por mês.

**Nível geográfico:** municipal.

**Fontes:**

- Banco Central do Brasil — Estatísticas do Pix.
- IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Links:**

- [Estatísticas do Pix — Banco Central](https://dadosabertos.bcb.gov.br/dataset/pix)
- [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** serviço Olinda do BCB, conjunto `TransacoesPixPorMunicipio`, utilizando o campo `VL_PagadorPF`, associado à população municipal.

**Limitações:**

O denominador é a população municipal, não o número de pagadores nem a quantidade de transações. Portanto, o indicador não representa ticket médio.

O volume movimentado por Pix é um fluxo de pagamentos: não equivale à renda, ao patrimônio ou ao saldo disponível dos moradores.

### Observação sobre a pontuação do I09

A definição por habitante está adotada no catálogo. Os parâmetros de normalização precisam acompanhar essa unidade; na metodologia V4.1, as âncoras herdadas da versão por pagador estão identificadas como pendentes de recalibração.

---

## Eixo 3 — Inclusão

Neste eixo, os indicadores são interpretados como referências de **demanda potencial de inclusão financeira**. Uma nota maior não significa, necessariamente, maior renda ou menor risco de crédito.

### I10 · Pessoas no CadÚnico por 100 habitantes

**O que queremos descobrir:**

Qual é a presença de pessoas cadastradas no CadÚnico em relação ao tamanho da população municipal?

**Dados necessários:**

- Quantidade de pessoas cadastradas no CadÚnico.
- População municipal.
- Município e código IBGE.
- Referência do cadastro e ano da população utilizada.

**Medida utilizada:** pessoas cadastradas divididas pela população, multiplicadas por 100.

**Nível geográfico:** municipal.

**Fontes:**

- Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome — bases agregadas do CadÚnico, MI Social/VIS DATA.
- IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Links:**

- [VIS DATA — MDS](https://aplicacoes.cidadania.gov.br/vis/)
- [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** extração dos dados agregados municipais de pessoas cadastradas, associados à população municipal.

**Limitações:**

O indicador conta pessoas, não famílias. Estar cadastrado no CadÚnico não significa, necessariamente, receber Bolsa Família.

Diferenças entre as referências cadastrais e populacionais podem produzir valores superiores a 100 por 100 habitantes, que devem ser investigados.

Não são necessárias consultas individuais por CPF ou NIS.

### I11 · Crédito PF per capita

**O que queremos descobrir:**

Qual é o volume de crédito de pessoas físicas por habitante, utilizado como referência de penetração do crédito?

**Dados necessários:**

- Carteira ativa de crédito de pessoas físicas da UF.
- População da UF.
- UF.
- Período da carteira e ano da população utilizada.

**Medida utilizada:** carteira ativa PF estadual dividida pela população estadual, em reais por habitante.

**Nível geográfico:** estadual, com estimativa municipal experimental pelo cofator.

**Fontes:**

- Banco Central do Brasil — SCR.data.
- IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Links:**

- [SCR.data — Banco Central](https://dadosabertos.bcb.gov.br/dataset/scr_data)
- [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** extração da carteira ativa PF por UF e associação com a população estadual.

**Limitações:**

O valor representa crédito por habitante, não a dívida média de cada tomador de crédito.

No eixo Inclusão, menor crédito per capita é utilizado como sinal de possível demanda de atendimento. Isso não comprova, isoladamente, demanda reprimida ou ausência de acesso.

O valor ajustado continua sendo uma estimativa municipal experimental.

### I12 · Informalidade derivada do Censo — proxy

**O que queremos descobrir:**

Qual é a participação de categorias ocupacionais utilizadas como aproximação da informalidade no município?

**Dados necessários:**

- Pessoas ocupadas nas categorias selecionadas pelo projeto.
- Total de pessoas ocupadas no mesmo universo.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** participação das categorias selecionadas no total de ocupados, em percentual.

**Nível geográfico:** municipal, sem aplicação do cofator.

**Fonte:** IBGE — Censo Demográfico 2022, SIDRA, tabela 10261.

**Link:** [SIDRA — Tabela 10261](https://sidra.ibge.gov.br/tabela/10261)

**Forma de obtenção:** consulta municipal à tabela, agregando as categorias ocupacionais definidas na extração do projeto.

**Limitações:**

É uma proxy, isto é, uma aproximação da informalidade. Não deve ser apresentada automaticamente como equivalente à taxa oficial de informalidade da PNAD Contínua.

As categorias utilizadas no numerador devem permanecer explicitadas no notebook para permitir a reprodução do cálculo.

---

## Eixo 4 — Demografia e infraestrutura

### I13 · Variação das estimativas populacionais

**O que queremos descobrir:**

Como o tamanho estimado da população municipal variou entre dois anos?

**Dados necessários:**

- População estimada no ano inicial.
- População estimada no ano final.
- Município e código IBGE.
- Anos de referência.

**Medida utilizada:** diferença entre as estimativas, dividida pela população do ano inicial, em percentual.

**Nível geográfico:** municipal.

**Fonte:** IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Link:** [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** consulta das estimativas municipais para os dois anos comparados. A base de referência utilizada na metodologia considera 2024 e 2025.

**Limitações:**

A variação pode refletir mudanças demográficas, revisões das estimativas e alterações territoriais. Não deve ser interpretada exclusivamente como crescimento natural ou migração.

### I14 · Participação na força de trabalho de 18 a 64 anos

**O que queremos descobrir:**

Qual parcela da população entre 18 e 64 anos participa da força de trabalho?

**Dados necessários:**

- Pessoas de 18 a 64 anos na força de trabalho.
- População total de 18 a 64 anos no mesmo universo.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** pessoas da faixa etária na força de trabalho divididas pela população da mesma faixa, em percentual.

**Nível geográfico:** municipal.

**Fonte:** IBGE — Censo Demográfico 2022, SIDRA, tabela 6580.

**Link:** [SIDRA — Tabela 6580](https://sidra.ibge.gov.br/tabela/6580)

**Forma de obtenção:** agregação dos grupos de 18 a 24 anos e de 25 a 64 anos, utilizando o mesmo recorte no numerador e no denominador.

**Limitações:**

A força de trabalho inclui pessoas ocupadas e desocupadas. O indicador mede participação, não taxa de emprego.

A faixa adotada é **18 a 64 anos**, substituindo as propostas anteriores de 15–64 ou 16–64 anos.

A participação econômica e o recorte etário passam a ser considerados conjuntamente, sem manter um indicador separado de estrutura etária no Score.

### I15 · População absoluta — informação complementar

**O que queremos descobrir:**

Qual é o porte populacional do município?

**Dados necessários:**

- População municipal estimada.
- Município e código IBGE.
- Ano de referência.

**Medida utilizada:** número de habitantes.

**Nível geográfico:** municipal.

**Fonte:** IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Link:** [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** consulta da população estimada por município e ano.

**Utilização no projeto:**

- Apresentação do porte populacional.
- Filtros e contextualização do ranking.
- Denominador dos indicadores calculados por habitante.

**Limitações:**

A população absoluta **não possui normalização, nota ou peso próprio no Score**. Seu uso como denominador em outros indicadores permanece.

É necessário identificar o ano da estimativa utilizada.

### I16 · Agências bancárias por 100 mil habitantes

**O que queremos descobrir:**

Qual é a densidade da oferta física de agências bancárias em relação à população municipal?

**Dados necessários:**

- Quantidade de agências bancárias no município.
- População municipal.
- Município e código de identificação.
- Data de referência das agências.
- Ano da população utilizada.

**Medida utilizada:** quantidade de agências dividida pela população, multiplicada por 100 mil.

**Nível geográfico:** municipal.

**Fontes:**

- Banco Central do Brasil — Agências de Instituições Supervisionadas.
- IBGE — estimativas populacionais, SIDRA, tabela 6579.

**Links:**

- [Agências de Instituições Supervisionadas — Banco Central](https://dadosabertos.bcb.gov.br/dataset/agencias-de-instituicoes-supervisionadas-pelo-bacen)
- [SIDRA — Tabela 6579](https://sidra.ibge.gov.br/tabela/6579)

**Forma de obtenção:** consulta à base de agências, contagem municipal e associação com a população.

**Limitações:**

A medida não contempla integralmente canais digitais, correspondentes bancários e outras formas de atendimento.

Na orientação adotada pelo projeto, menor densidade recebe maior pontuação por indicar possível necessidade de alternativas de acesso. Isso não comprova, isoladamente, exclusão financeira ou capacidade de pagamento.

---

## Documentação complementar

- [Metodologia do Score: fórmulas, normalização e pesos](./score.md)
- [Cofator de reajuste: aplicação aos indicadores estaduais](./cofator.md)
