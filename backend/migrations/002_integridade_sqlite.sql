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
