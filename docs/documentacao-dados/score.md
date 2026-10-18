# Metodologia do score KREDITA

## O que o score representa?

O score KREDITA combina indicadores socioeconômicos e financeiros para comparar municípios, considerando tanto suas condições econômicas quanto a demanda potencial de inclusão financeira.

O resultado varia de **0 a 100**. Uma pontuação maior representa maior aderência aos critérios definidos pelo projeto, **não uma probabilidade de pagamento ou uma classificação individual de crédito**.

A metodologia utiliza **15 indicadores na pontuação**, organizados em quatro eixos. A população absoluta é apresentada como informação complementar, sem peso próprio no resultado.

## Quatro perguntas, quatro eixos

| Pergunta | Eixo | O que considera |
| --- | --- | --- |
| **Quais condições sinalizam menor risco?** | E1 · Risco | Inadimplência, fragilidade de renda e composição dos saldos vencidos |
| **Quais condições sustentam a atividade financeira?** | E2 · Capacidade financeira e atividade | Trabalho, salários, renda, crédito e pagamentos Pix |
| **Onde existe maior demanda potencial de inclusão?** | E3 · Inclusão | Presença no CadÚnico, penetração de crédito e informalidade |
| **Como a população e a infraestrutura caracterizam o município?** | E4 · Demografia e infraestrutura | Variação populacional, participação no trabalho e oferta física bancária |

> Uma nota alta tem significado próprio em cada eixo. Em Risco, representa condições consideradas menos arriscadas; em Inclusão, representa maior demanda potencial de atendimento. O score final combina essas perspectivas.

## Da informação à pontuação

O cálculo segue cinco etapas:

1. **Valor bruto:** obtenção ou cálculo do indicador a partir da fonte.
2. **Ajuste estadual:** aplicação do cofator aos indicadores I01, I03, I08 e I11.
3. **Normalização:** transformação dos valores em notas comparáveis.
4. **Nota do eixo:** média ponderada dos indicadores daquele eixo.
5. **Score final:** média dos eixos selecionados, com pesos iguais entre eles.

A metodologia do ajuste está descrita em [Cofator de reajuste](./cofator.md). Neste documento, sua aplicação aparece diretamente nas fórmulas dos quatro indicadores envolvidos.

### Como ler as fórmulas

- **x:** valor bruto do indicador.
- **φ:** cofator de reajuste.
- **z:** estimativa municipal experimental após aplicar o cofator ao valor estadual.
- **N:** nota normalizada do indicador.
- **clip(valor; mínimo; máximo):** mantém o resultado dentro do intervalo indicado.
- **ln:** logaritmo natural.
- **t:** valor limitado ao intervalo definido para uma fórmula logarítmica.

Nos indicadores **I01, I03, I08 e I11**, a normalização utiliza **z**, após o ajuste. Nos demais indicadores pontuados, utiliza diretamente **x**.

Nas fórmulas percentuais, um valor de 5% é informado como **5**. O cofator utiliza representação decimal: por exemplo, **8% = 0,08**.

**Os limites e as âncoras de normalização são parâmetros experimentais da versão atual.** Não representam automaticamente médias nacionais, percentis ou limites oficiais das fontes.

## E1 · Risco

### I01 · Inadimplência PF

Representa a parcela da carteira de crédito de pessoas físicas associada a operações inadimplentes. Acrescenta ao eixo uma referência sobre o risco de crédito.

**1. Valor bruto estadual:**

```text
x = 100 × carteira inadimplente PF / carteira ativa PF
```

**2. Aplicação do cofator:**

```text
z = x × (1 − φ)
```

**3. Normalização:**

```text
N01 = clip(100 × (6,5 − z) / 4,5; 0; 100)
```

Menores valores ajustados recebem notas maiores.

**Fonte:** BCB SCR.data — dezembro de 2025, recorte estadual.

> A carteira inadimplente não deve ser confundida com o saldo das parcelas vencidas utilizado no I03.

### I02 · Fragilidade de renda

Representa a proporção de pessoas em domicílios com renda per capita de até meio salário mínimo. Considera a vulnerabilidade econômica que pode limitar a capacidade de absorver despesas e compromissos financeiros.

**1. Valor bruto municipal:**

```text
x = 100 × pessoas em domicílios com renda per capita até 0,5 salário mínimo
          / pessoas no universo da tabela
```

**2. Normalização:**

```text
N02 = clip(100 × (68 − x) / 60; 0; 100)
```

Menor fragilidade de renda recebe nota maior.

**Fonte:** IBGE, Censo 2022 — SIDRA, tabela 10296.

### I03 · Composição dos saldos vencidos 90+

Representa a concentração dos saldos vencidos nos atrasos superiores a 90 dias. Complementa o I01 ao considerar a composição dos atrasos, em vez da participação da carteira inadimplente na carteira total.

**1. Valor bruto estadual:**

```text
x = 100 × saldo vencido acima de 90 dias
          / (saldo vencido de 15 a 90 dias + saldo vencido acima de 90 dias)
```

**2. Aplicação do cofator:**

```text
z = x × (1 − φ)
```

**3. Normalização:**

```text
N03 = clip(100 × (82 − z) / 27; 0; 100)
```

Menor concentração ajustada nos atrasos mais longos recebe nota maior.

**Fonte:** BCB SCR.data — dezembro de 2025, operações PF, recorte estadual.

## E2 · Capacidade financeira e atividade

### I04 · Desocupação

Representa a proporção de desocupados na força de trabalho de 14 anos ou mais. Indica dificuldades de inserção no mercado de trabalho.

**1. Valor bruto municipal:**

```text
x = 100 × pessoas desocupadas / pessoas na força de trabalho
```

**2. Normalização:**

```text
N04 = clip(100 × (18 − x) / 16,5; 0; 100)
```

Menor desocupação recebe nota maior. Pessoas fora da força de trabalho não entram como desocupadas.

**Fonte:** IBGE, Censo 2022 — SIDRA, tabela 9517.

### I05 · Salário médio de admissão mensal

Representa a remuneração média informada nas novas contratações formais com salário mensal válido. Acrescenta uma referência sobre a qualidade remuneratória das admissões recentes.

**1. Valor bruto municipal:**

```text
x = soma dos salários mensais válidos das admissões
    / quantidade dessas admissões válidas
```

**2. Normalização:**

```text
t = clip(x; 1500; 4500)

N05 = 100 × ln(t / 1500) / ln(4500 / 1500)
```

Salários maiores recebem notas maiores, com escala logarítmica.

**Fonte:** MTE, Novo CAGED — movimentações de dezembro de 2025.

> Esse indicador não representa o salário médio de todos os trabalhadores. Sem admissões com salário válido, o dado é ausente.

### I06 · Saldo formal por mil habitantes

Representa a expansão ou retração dos vínculos formais no mês, proporcionalmente à população municipal.

**1. Valor bruto municipal:**

```text
x = 1000 × (admissões − desligamentos) / população municipal
```

**2. Normalização:**

```text
N06 = clip(50 + 50 × x / 15; 0; 100)
```

Saldo zero recebe nota 50. Saldos positivos ficam acima de 50 e negativos abaixo de 50, respeitados os limites da escala.

**Fontes:** MTE, Novo CAGED — dezembro de 2025; IBGE, SIDRA 6579 — população estimada de 2025.

> O resultado mensal pode ser influenciado pela sazonalidade das contratações e dos desligamentos.

### I07 · Renda domiciliar per capita

Representa os recursos domiciliares por pessoa. Complementa os indicadores de emprego ao considerar a renda no âmbito dos domicílios.

**1. Valor bruto municipal:**

Rendimento nominal médio mensal domiciliar per capita publicado pelo IBGE.

**2. Normalização:**

```text
t = clip(x; 350; 3200)

Se t ≤ 1050:
N07 = 50 × ln(t / 350) / ln(1050 / 350)

Se t > 1050:
N07 = 50 + 50 × ln(t / 1050) / ln(3200 / 1050)
```

A escala atribui nota 0 a R$ 350, nota 50 a R$ 1.050 e nota 100 a R$ 3.200, com progressão logarítmica entre essas referências.

**Fonte:** IBGE, Censo 2022 — SIDRA, tabela 10295.

> Os valores são nominais de 2022. R$ 1.050 é uma âncora do modelo, não uma média nacional calculada nesta versão.

### I08 · Crédito/depósitos

Representa a relação entre o volume de crédito e os depósitos bancários. Na hipótese adotada pelo projeto, uma razão maior favorece a nota de capacidade financeira.

**1. Valor bruto estadual:**

```text
x = crédito total da UF / depósitos totais da UF
```

Na extração utilizada, o crédito corresponde ao verbete 160 e os depósitos à soma dos verbetes 401, 420 e 432.

**2. Aplicação do cofator:**

```text
z = x × (1 + φ)
```

**3. Normalização:**

```text
N08 = clip(100 × (z − 0,4) / 1,2; 0; 100)
```

Maiores valores ajustados recebem notas maiores.

**Fonte:** BCB, ESTBAN — dezembro de 2025, valores agregados por UF.

> Essa relação não é uma medida prudencial de liquidez. Sua orientação crescente é uma escolha do modelo.

### I09 · Volume Pix pago por PF por habitante

Representa a intensidade dos pagamentos Pix realizados por pessoas físicas em relação ao número de residentes. Acrescenta uma dimensão de movimentação financeira ao eixo.

**1. Valor bruto municipal:**

```text
x = valor mensal de Pix pago por PF / população municipal
```

Unidade: **R$/habitante/mês**. O denominador é a população, não o número de pagadores.

**2. Normalização:**

```text
t = clip(x; 2200; 14000)

Se t ≤ 6000:
N09 = 50 × ln(t / 2200) / ln(6000 / 2200)

Se t > 6000:
N09 = 50 + 50 × ln(t / 6000) / ln(14000 / 6000)
```

**Fontes:** BCB, Olinda Pix, conjunto `TransacoesPixPorMunicipio`, campo `VL_PagadorPF` — dezembro de 2025; IBGE, SIDRA 6579 — população de 2025.

> Volume Pix é fluxo de pagamentos, não renda ou saldo disponível. As âncoras atuais foram mantidas da versão por pagador e precisam de recalibração para a definição por habitante.

## E3 · Inclusão

### I10 · Densidade cadastral

Representa o número de pessoas cadastradas no CadÚnico por 100 habitantes. É utilizado como referência de demanda potencial de inclusão.

**1. Valor bruto municipal:**

```text
x = 100 × pessoas no CadÚnico / população municipal
```

**2. Normalização:**

```text
N10 = clip(100 × (x − 15) / 60; 0; 100)
```

Maior densidade cadastral recebe nota maior no eixo Inclusão.

**Fontes:** MDS, MI Social — dezembro de 2025; IBGE, SIDRA 6579 — população de 2025.

> A contagem é de pessoas, não de famílias. Diferenças cadastrais e temporais podem produzir valores superiores a 100 por 100 habitantes, que exigem análise da base.

### I11 · Crédito PF per capita

Representa o volume de crédito de pessoas físicas em relação à população estadual. O modelo utiliza menor penetração de crédito como sinal de demanda potencial de inclusão.

**1. Valor bruto estadual:**

```text
x = carteira ativa PF da UF / população da UF
```

**2. Aplicação do cofator:**

```text
z = x × (1 − φ)
```

**3. Normalização:**

```text
t = clip(z; 2000; 22000)

N11 = 100 × ln(22000 / t) / ln(22000 / 2000)
```

Menores valores ajustados recebem notas maiores no eixo Inclusão.

**Fontes:** BCB, SCR.data — dezembro de 2025; IBGE, SIDRA 6579 — população estadual de 2025.

> Menor crédito per capita não comprova, isoladamente, demanda reprimida ou ausência de acesso. Essa interpretação é uma hipótese do modelo.

### I12 · Informalidade derivada do Censo

Representa a participação de categorias ocupacionais selecionadas como aproximação da informalidade. Acrescenta ao eixo a presença de trabalhadores potencialmente menos atendidos pelos mecanismos tradicionais de crédito.

**1. Valor bruto municipal:**

```text
x = 100 × ocupados nas categorias selecionadas como proxy de informalidade
          / ocupados totais
```

**2. Normalização:**

```text
Se x ≤ 39:
N12 = clip(30 + 20 × (x − 25) / 14; 30; 50)

Se x > 39:
N12 = clip(50 + 50 × (x − 39) / 21; 50; 100)
```

A escala possui piso de 30 pontos, nota 50 em 39% e nota 100 a partir de 60%. Maior informalidade favorece a nota de demanda de inclusão.

**Fonte:** IBGE, Censo 2022 — SIDRA, tabela 10261.

> É uma aproximação baseada nas categorias selecionadas, não uma reprodução automática da definição de informalidade da PNAD. O valor de 39% é uma âncora experimental.

## E4 · Demografia e infraestrutura

### I13 · Variação das estimativas populacionais

Representa a mudança estimada do tamanho da população entre dois anos. Acrescenta uma referência de dinâmica demográfica.

**1. Valor bruto municipal:**

```text
x = 100 × (população de 2025 − população de 2024) / população de 2024
```

**2. Normalização:**

```text
N13 = clip(100 × (x + 1,5) / 4; 0; 100)
```

Maior variação recebe nota maior, no intervalo de referência de −1,5% a +2,5%.

**Fonte:** IBGE — SIDRA, tabela 6579, estimativas de 2024 e 2025.

> A variação pode refletir revisões das estimativas e alterações territoriais, além de mudanças demográficas.

### I14 · Participação na força de trabalho de 18 a 64 anos

Representa a parcela da população dessa faixa etária que participa da força de trabalho. Permite considerar a participação econômica, em vez de apenas o tamanho da população em idade ativa.

**1. Valor bruto municipal:**

```text
x = 100 × pessoas de 18 a 64 anos na força de trabalho
          / população de 18 a 64 anos
```

**2. Normalização:**

```text
N14 = clip(100 × (x − 42) / 28; 0; 100)
```

Maior participação recebe nota maior.

**Fonte:** IBGE, Censo 2022 — SIDRA, tabela 6580, agregação dos grupos de 18–24 e 25–64 anos.

> A força de trabalho inclui ocupados e desocupados. A faixa utilizada é 18–64 anos, não 16–64.

### I15 · População absoluta — informação complementar

Apresenta o porte populacional do município e permite aplicar filtros ao ranking.

**Valor:** população municipal estimada de 2025.

**Fonte:** IBGE — SIDRA, tabela 6579.

**Não possui normalização, nota ou peso no score.** A população continua sendo utilizada como denominador nos indicadores que exigem esse cálculo.

### I16 · Agências por 100 mil habitantes

Representa a densidade da oferta física bancária. Na orientação adotada, menor presença de agências recebe maior nota por indicar possível necessidade de alternativas de acesso.

**1. Valor bruto municipal:**

```text
x = 100000 × número de agências / população municipal
```

**2. Normalização:**

```text
N16 = clip(100 × (20 − x) / 20; 0; 100)
```

Menor densidade recebe nota maior.

**Fontes:** BCB, Informes de Agências — referência de 13/10/2026; IBGE, SIDRA 6579 — população de 2025.

> O indicador não contempla todo o acesso digital ou por correspondentes. Menor presença física não comprova, isoladamente, exclusão financeira ou capacidade de pagamento.

## Composição das notas dos eixos

Cada eixo utiliza uma **média ponderada**: as notas dos indicadores são multiplicadas pelos respectivos pesos e depois somadas.

As notas **N01, N03, N08 e N11** já incorporam o ajuste do cofator antes da normalização. Portanto, o cofator não é aplicado novamente na média dos eixos ou no score final.

### Pesos dentro de cada eixo

| Eixo | Indicador | Peso no eixo |
| --- | --- | ---: |
| E1 · Risco | I01 · Inadimplência PF | 40% |
| E1 · Risco | I02 · Fragilidade de renda | 25% |
| E1 · Risco | I03 · Composição dos saldos vencidos 90+ | 35% |
| E2 · Capacidade financeira e atividade | I04 · Desocupação | 1/6 |
| E2 · Capacidade financeira e atividade | I05 · Salário médio de admissão | 1/6 |
| E2 · Capacidade financeira e atividade | I06 · Saldo formal por mil habitantes | 1/6 |
| E2 · Capacidade financeira e atividade | I07 · Renda domiciliar per capita | 1/6 |
| E2 · Capacidade financeira e atividade | I08 · Crédito/depósitos | 1/6 |
| E2 · Capacidade financeira e atividade | I09 · Pix por habitante | 1/6 |
| E3 · Inclusão | I10 · Densidade cadastral | 40% |
| E3 · Inclusão | I11 · Crédito PF per capita | 40% |
| E3 · Inclusão | I12 · Informalidade | 20% |
| E4 · Demografia e infraestrutura | I13 · Variação populacional | 20% |
| E4 · Demografia e infraestrutura | I14 · Participação na força de trabalho | 40% |
| E4 · Demografia e infraestrutura | I16 · Agências por 100 mil habitantes | 40% |

No E2, **1/6 equivale a aproximadamente 16,67%**. O cálculo utiliza a fração exata.

### Fórmulas dos eixos

```text
E1 = 0,40 × N01 + 0,25 × N02 + 0,35 × N03

E2 = (N04 + N05 + N06 + N07 + N08 + N09) / 6

E3 = 0,40 × N10 + 0,40 × N11 + 0,20 × N12

E4 = 0,20 × N13 + 0,40 × N14 + 0,40 × N16
```

## Composição do score final

Com os quatro eixos selecionados, cada um representa **25% do resultado**:

```text
Score = 0,25 × E1 + 0,25 × E2 + 0,25 × E3 + 0,25 × E4

Score = (E1 + E2 + E3 + E4) / 4
```

## Material explicativo completo

Para aprofundar a leitura, consulte o PDF com o detalhamento das fórmulas, dos pesos, das etapas de cálculo e dos exemplos de aplicação:

📄 [Ler o PDF — Metodologia do Score KREDITA V4](https://cdn.discordapp.com/attachments/1544375422517772355/1561155747415334982/KREDITA_Metodologia_Score_V4.pdf?ex=6ad5fbd7&is=6ad4aa57&hm=704d2a1f7626c64a71d518668762d2bb08f39a97f349cd26ae57ba4c57f10a1f&)
