CREATE TABLE IF NOT EXISTS municipios (
    codigo_ibge text PRIMARY KEY CHECK (length(codigo_ibge) = 7 AND codigo_ibge GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    nome text NOT NULL,
    uf text NOT NULL CHECK (length(uf) = 2 AND uf GLOB '[A-Z][A-Z]'),
    regiao text NOT NULL
);

CREATE TABLE IF NOT EXISTS indicadores (
    codigo text PRIMARY KEY CHECK (length(codigo) = 3 AND codigo GLOB 'i[0-9][0-9]'),
    nome text NOT NULL,
    unidade text NOT NULL
);

CREATE TABLE IF NOT EXISTS lotes_importacao (
    id integer PRIMARY KEY AUTOINCREMENT,
    hash text NOT NULL UNIQUE,
    arquivos text NOT NULL,
    importado_em text NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS observacoes (
    id integer PRIMARY KEY AUTOINCREMENT,
    indicador text NOT NULL REFERENCES indicadores,
    municipio text REFERENCES municipios,
    uf text CHECK (uf IS NULL OR (length(uf) = 2 AND uf GLOB '[A-Z][A-Z]')),
    fonte text NOT NULL,
    referencia text NOT NULL,
    valor_bruto double precision,
    situacao text NOT NULL CHECK (situacao IN ('observado', 'estimado', 'ausente')),
    lote_id integer NOT NULL REFERENCES lotes_importacao,
    hash text NOT NULL UNIQUE,
    UNIQUE (id, indicador),
    CHECK ((municipio IS NULL) <> (uf IS NULL)),
    CHECK ((situacao = 'ausente') = (valor_bruto IS NULL))
);

CREATE TABLE IF NOT EXISTS edicoes_score (
    id integer PRIMARY KEY AUTOINCREMENT,
    lote_id integer NOT NULL REFERENCES lotes_importacao,
    competencia text NOT NULL CHECK (length(competencia) = 10 AND substr(competencia, 9, 2) = '01'),
    calculado_em text,
    publicado_em text NOT NULL DEFAULT (datetime('now')),
    versao text NOT NULL,
    configuracao text NOT NULL,
    tipo text NOT NULL CHECK (tipo IN ('publicado', 'simulacao_scr')),
    UNIQUE (lote_id, tipo, competencia)
);

CREATE INDEX IF NOT EXISTS edicoes_publicadas_idx
    ON edicoes_score (competencia DESC, id DESC)
    WHERE tipo = 'publicado';

CREATE TABLE IF NOT EXISTS scores_municipais (
    edicao_id integer REFERENCES edicoes_score,
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
    edicao_id integer,
    codigo_ibge text,
    indicador text REFERENCES indicadores,
    observacao_id integer NOT NULL,
    nome text NOT NULL,
    unidade text NOT NULL,
    valor_usado double precision,
    nota double precision CHECK (nota BETWEEN 0 AND 100),
    nota_sem_cofator double precision CHECK (nota_sem_cofator BETWEEN 0 AND 100),
    peso double precision NOT NULL CHECK (peso BETWEEN 0 AND 1),
    reaproveitado boolean NOT NULL DEFAULT 0,
    zero_i06_confirmado boolean NOT NULL DEFAULT 0,
    PRIMARY KEY (edicao_id, codigo_ibge, indicador),
    FOREIGN KEY (edicao_id, codigo_ibge) REFERENCES scores_municipais,
    FOREIGN KEY (observacao_id, indicador) REFERENCES observacoes (id, indicador)
);

CREATE TABLE IF NOT EXISTS observacoes_historicas (
    observacao_id integer NOT NULL REFERENCES observacoes,
    versao text NOT NULL,
    unidade text NOT NULL,
    PRIMARY KEY (observacao_id, versao, unidade)
);

CREATE TABLE IF NOT EXISTS estudos_apostas (
    id text PRIMARY KEY,
    estudo text NOT NULL,
    inicio text NOT NULL,
    fim text NOT NULL CHECK (fim >= inicio),
    metrica text NOT NULL,
    unidade text NOT NULL,
    fonte text NOT NULL
);

CREATE TABLE IF NOT EXISTS estimativas_apostas (
    estudo_id text REFERENCES estudos_apostas,
    uf text CHECK (length(uf) = 2 AND uf GLOB '[A-Z][A-Z]'),
    valor double precision NOT NULL CHECK (valor BETWEEN 0 AND 100),
    margem_pp double precision CHECK (margem_pp BETWEEN 0 AND 100),
    populacao_estimada integer CHECK (populacao_estimada >= 0),
    PRIMARY KEY (estudo_id, uf)
);

CREATE TRIGGER IF NOT EXISTS municipios_codigo_obrigatorio_insert
BEFORE INSERT ON municipios
WHEN NEW.codigo_ibge IS NULL
BEGIN
    SELECT RAISE(ABORT, 'Código IBGE obrigatório');
END;

CREATE TRIGGER IF NOT EXISTS municipios_codigo_obrigatorio_update
BEFORE UPDATE OF codigo_ibge ON municipios
WHEN NEW.codigo_ibge IS NULL
BEGIN
    SELECT RAISE(ABORT, 'Código IBGE obrigatório');
END;

CREATE TRIGGER IF NOT EXISTS edicoes_competencia_valida_insert
BEFORE INSERT ON edicoes_score
WHEN NEW.competencia NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-01'
     OR substr(NEW.competencia, 1, 4) = '0000'
     OR substr(NEW.competencia, 6, 2) NOT BETWEEN '01' AND '12'
BEGIN
    SELECT RAISE(ABORT, 'Competência inválida. Use AAAA-MM-01');
END;

CREATE TRIGGER IF NOT EXISTS edicoes_competencia_valida_update
BEFORE UPDATE OF competencia ON edicoes_score
WHEN NEW.competencia NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-01'
     OR substr(NEW.competencia, 1, 4) = '0000'
     OR substr(NEW.competencia, 6, 2) NOT BETWEEN '01' AND '12'
BEGIN
    SELECT RAISE(ABORT, 'Competência inválida. Use AAAA-MM-01');
END;
