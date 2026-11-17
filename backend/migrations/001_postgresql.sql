CREATE TABLE IF NOT EXISTS municipios (
    codigo_ibge text PRIMARY KEY CHECK (codigo_ibge ~ '^[0-9]{7}$'),
    nome text NOT NULL,
    uf text NOT NULL CHECK (uf ~ '^[A-Z]{2}$'),
    regiao text NOT NULL
);

CREATE TABLE IF NOT EXISTS indicadores (
    codigo text PRIMARY KEY CHECK (codigo ~ '^i[0-9]{2}$'),
    nome text NOT NULL,
    unidade text NOT NULL
);

CREATE TABLE IF NOT EXISTS lotes_importacao (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hash text NOT NULL UNIQUE,
    arquivos jsonb NOT NULL,
    importado_em timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS observacoes (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    indicador text NOT NULL REFERENCES indicadores,
    municipio text REFERENCES municipios,
    uf text CHECK (uf ~ '^[A-Z]{2}$'),
    fonte text NOT NULL,
    referencia text NOT NULL,
    valor_bruto double precision,
    situacao text NOT NULL CHECK (situacao IN ('observado', 'estimado', 'ausente')),
    lote_id bigint NOT NULL REFERENCES lotes_importacao,
    hash text NOT NULL UNIQUE,
    UNIQUE (id, indicador),
    CHECK ((municipio IS NULL) <> (uf IS NULL)),
    CHECK ((situacao = 'ausente') = (valor_bruto IS NULL))
);

CREATE TABLE IF NOT EXISTS edicoes_score (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id bigint NOT NULL REFERENCES lotes_importacao,
    competencia date NOT NULL CHECK (extract(day FROM competencia) = 1),
    calculado_em timestamptz,
    publicado_em timestamptz NOT NULL DEFAULT now(),
    versao text NOT NULL,
    configuracao jsonb NOT NULL,
    tipo text NOT NULL CHECK (tipo IN ('publicado', 'simulacao_scr')),
    UNIQUE (lote_id, tipo, competencia)
);

CREATE INDEX IF NOT EXISTS edicoes_publicadas_idx
    ON edicoes_score (competencia DESC, id DESC)
    WHERE tipo = 'publicado';

CREATE TABLE IF NOT EXISTS scores_municipais (
    edicao_id bigint REFERENCES edicoes_score,
    codigo_ibge text REFERENCES municipios,
    populacao double precision CHECK (populacao >= 0),
    score double precision CHECK (score BETWEEN 0 AND 100),
    score_sem_cofator double precision CHECK (score_sem_cofator BETWEEN 0 AND 100),
    e1 double precision CHECK (e1 BETWEEN 0 AND 100),
    e2 double precision CHECK (e2 BETWEEN 0 AND 100),
    e3 double precision CHECK (e3 BETWEEN 0 AND 100),
    e4 double precision CHECK (e4 BETWEEN 0 AND 100),
    cofator double precision CHECK (cofator BETWEEN -0.2 AND 0.2),
    m double precision CHECK (m BETWEEN 0 AND 100),
    pos_brasil integer CHECK (pos_brasil > 0),
    pos_uf integer CHECK (pos_uf > 0),
    pos_regiao integer CHECK (pos_regiao > 0),
    motivo_sem_score text,
    PRIMARY KEY (edicao_id, codigo_ibge),
    CHECK (score IS NOT NULL OR
           (pos_brasil IS NULL AND pos_uf IS NULL AND pos_regiao IS NULL))
);

CREATE INDEX IF NOT EXISTS scores_historico_idx
    ON scores_municipais (codigo_ibge, edicao_id);
CREATE INDEX IF NOT EXISTS scores_ranking_idx
    ON scores_municipais (edicao_id, pos_brasil, codigo_ibge)
    WHERE score IS NOT NULL;

CREATE TABLE IF NOT EXISTS score_indicadores (
    edicao_id bigint,
    codigo_ibge text,
    indicador text REFERENCES indicadores,
    observacao_id bigint NOT NULL,
    nome text NOT NULL,
    unidade text NOT NULL,
    valor_usado double precision,
    nota double precision CHECK (nota BETWEEN 0 AND 100),
    nota_sem_cofator double precision CHECK (nota_sem_cofator BETWEEN 0 AND 100),
    peso double precision NOT NULL CHECK (peso BETWEEN 0 AND 1),
    reaproveitado boolean NOT NULL DEFAULT false,
    zero_i06_confirmado boolean NOT NULL DEFAULT false,
    PRIMARY KEY (edicao_id, codigo_ibge, indicador),
    FOREIGN KEY (edicao_id, codigo_ibge) REFERENCES scores_municipais,
    FOREIGN KEY (observacao_id, indicador) REFERENCES observacoes (id, indicador)
);

ALTER TABLE score_indicadores ADD COLUMN IF NOT EXISTS reaproveitado boolean NOT NULL DEFAULT false;
ALTER TABLE score_indicadores ADD COLUMN IF NOT EXISTS zero_i06_confirmado boolean NOT NULL DEFAULT false;

CREATE TABLE IF NOT EXISTS observacoes_historicas (
    observacao_id bigint NOT NULL REFERENCES observacoes,
    versao text NOT NULL,
    unidade text NOT NULL,
    PRIMARY KEY (observacao_id, versao, unidade)
);

CREATE TABLE IF NOT EXISTS estudos_apostas (
    id text PRIMARY KEY,
    estudo text NOT NULL,
    inicio date NOT NULL,
    fim date NOT NULL CHECK (fim >= inicio),
    metrica text NOT NULL,
    unidade text NOT NULL,
    fonte text NOT NULL
);

CREATE TABLE IF NOT EXISTS estimativas_apostas (
    estudo_id text REFERENCES estudos_apostas,
    uf text CHECK (uf ~ '^[A-Z]{2}$'),
    valor double precision NOT NULL CHECK (valor BETWEEN 0 AND 100),
    margem_pp double precision CHECK (margem_pp BETWEEN 0 AND 100),
    populacao_estimada bigint CHECK (populacao_estimada >= 0),
    PRIMARY KEY (estudo_id, uf)
);
