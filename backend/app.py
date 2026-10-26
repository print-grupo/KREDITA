from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import json

app = Flask(__name__)

CSV_MUNICIPIOS = 'score_kredita_municipios.csv'
CSV_AUDITORIA = 'indicadores_auditoria.csv'
JSON_KREDITA = 'score_kredita.json'

try:
    df_municipios = pd.read_csv(CSV_MUNICIPIOS)
    if 'cod_municipio' in df_municipios.columns and 'cod_ibge' not in df_municipios.columns:
        df_municipios['cod_ibge'] = pd.to_numeric(df_municipios['cod_municipio'], errors='coerce')
    if 'populacao' in df_municipios.columns and 'pop2025' not in df_municipios.columns:
        df_municipios['pop2025'] = df_municipios['populacao']
    if 'score_kredita' in df_municipios.columns and 'score_dinamico' not in df_municipios.columns:
        df_municipios['score_dinamico'] = df_municipios['score_kredita']
except Exception as e:
    print(f"Erro ao carregar '{CSV_MUNICIPIOS}': {e}")
    df_municipios = pd.DataFrame()

try:
    df_auditoria = pd.read_csv(CSV_AUDITORIA)
    if 'cod_municipio' in df_auditoria.columns and 'cod_ibge' not in df_auditoria.columns:
        df_auditoria['cod_ibge'] = pd.to_numeric(df_auditoria['cod_municipio'], errors='coerce')
except Exception as e:
    df_auditoria = pd.DataFrame()

# Carregamento do JSON para mapear o score sem cofator (valor bruto / notas originais)
data_json_municipios = {}
try:
    with open(JSON_KREDITA, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
        for m in data_json.get('municipios', []):
            cod = int(m['cod_municipio'])
            notas_originais = m.get('notas', {}).copy()
            ajustes = m.get('ajustes_estaduais', {})
            for ind, adj in ajustes.items():
                if 'originalNote' in adj:
                    notas_originais[ind] = adj['originalNote']
            
            eixos_map = {
                'E1': ['i01', 'i02', 'i03'],
                'E2': ['i04', 'i05', 'i06', 'i07', 'i08', 'i09'],
                'E3': ['i10', 'i11', 'i12'],
                'E4': ['i13', 'i14', 'i15', 'i16']
            }
            
            # Cálculo do score bruto global (sem eixos filtrados específicos)
            vals_all = []
            for inds in eixos_map.values():
                for i in inds:
                    v = notas_originais.get(i)
                    if v is not None:
                        vals_all.append(v)
            score_bruto_global = sum(vals_all) / len(vals_all) if vals_all else m.get('score_kredita', 50.0)
            
            data_json_municipios[cod] = {
                'score_bruto_global': score_bruto_global,
                'json_obj': m
            }
except Exception:
    pass

@app.route('/')
def index():
    if df_municipios.empty:
        return "Erro: O arquivo de municípios não foi carregado corretamente.", 500

    busca = request.args.get('busca', '').strip()
    regiao_filtro = request.args.get('regiao', 'todas')
    ordem_filtro = request.args.get('ordem', 'maior_score')
    
    eixos_selecionados = request.args.getlist('eixos')
    if not eixos_selecionados and not request.args:
        eixos_selecionados = ['E1', 'E2', 'E3', 'E4']

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    per_page = 50
    df_filtrado = df_municipios.copy()

    for eixo in ['E1', 'E2', 'E3', 'E4']:
        if eixo not in df_filtrado.columns:
            df_filtrado[eixo] = 50.0
        else:
            df_filtrado[eixo] = pd.to_numeric(df_filtrado[eixo], errors='coerce').fillna(50.0)

    # Score atual (com valor ajustado)
    if eixos_selecionados:
        df_filtrado['score_dinamico'] = df_filtrado[eixos_selecionados].mean(axis=1)
    else:
        df_filtrado['score_dinamico'] = df_filtrado[['E1', 'E2', 'E3', 'E4']].mean(axis=1)

    # Sem cofator (com valor bruto / notas originais)
    def calc_score_bruto(cod, ativos):
        info = data_json_municipios.get(int(cod))
        if not info:
            return 50.0
        mun_json = info['json_obj']
        notas_originais = mun_json.get('notas', {}).copy()
        ajustes = mun_json.get('ajustes_estaduais', {})
        for ind, adj in ajustes.items():
            if 'originalNote' in adj:
                notas_originais[ind] = adj['originalNote']
        
        eixos_map = {
            'E1': ['i01', 'i02', 'i03'],
            'E2': ['i04', 'i05', 'i06', 'i07', 'i08', 'i09'],
            'E3': ['i10', 'i11', 'i12'],
            'E4': ['i13', 'i14', 'i15', 'i16']
        }
        
        valores_eixos = []
        for e in ativos:
            inds = eixos_map.get(e, [])
            vals = [notas_originais.get(i) for i in inds if notas_originais.get(i) is not None]
            if vals:
                valores_eixos.append(sum(vals) / len(vals))
            else:
                valores_eixos.append(50.0)
        return sum(valores_eixos) / len(valores_eixos) if valores_eixos else 50.0

    df_filtrado['score_sem_cofator'] = df_filtrado.apply(lambda r: calc_score_bruto(r['cod_ibge'], eixos_selecionados), axis=1)

    if busca:
        df_filtrado = df_filtrado[df_filtrado['municipio'].str.contains(busca, case=False, na=False)]

    if regiao_filtro and regiao_filtro != 'todas':
        df_filtrado = df_filtrado[df_filtrado['regiao'].str.strip().str.lower() == regiao_filtro.strip().lower()]

    try:
        pop_min = float(request.args.get('pop_min')) if request.args.get('pop_min', '').strip() else None
    except ValueError:
        pop_min = None

    try:
        pop_max = float(request.args.get('pop_max')) if request.args.get('pop_max', '').strip() else None
    except ValueError:
        pop_max = None

    if pop_min is not None:
        df_filtrado = df_filtrado[df_filtrado['pop2025'] >= pop_min]
    if pop_max is not None:
        df_filtrado = df_filtrado[df_filtrado['pop2025'] <= pop_max]

    if ordem_filtro == 'maior_score':
        df_filtrado = df_filtrado.sort_values(by='score_dinamico', ascending=False)
    elif ordem_filtro == 'menor_score':
        df_filtrado = df_filtrado.sort_values(by='score_dinamico', ascending=True)
    elif ordem_filtro == 'nome':
        df_filtrado = df_filtrado.sort_values(by='municipio', ascending=True)

    total_municipios = len(df_filtrado)
    total_pages = max(1, (total_municipios + per_page - 1) // per_page)
    
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    df_paginado = df_filtrado.iloc[start_idx:end_idx]
    ranking_lista = df_paginado.to_dict(orient='records')
    regioes_disponiveis = ['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste']

    return render_template(
        'index.html',
        ranking=ranking_lista,
        total_municipios=total_municipios,
        regioes=regioes_disponiveis,
        busca_atual=busca,
        regiao_atual=regiao_filtro,
        pop_min_atual=request.args.get('pop_min', ''),
        pop_max_atual=request.args.get('pop_max', ''),
        ordem_atual=ordem_filtro,
        eixos_ativos=eixos_selecionados,
        page=page,
        total_pages=total_pages,
        start_idx=start_idx
    )

@app.route('/municipio/<int:cod_ibge>')
def municipio_detalhe(cod_ibge):
    mun_dados = df_municipios[df_municipios['cod_ibge'] == cod_ibge]
    
    if mun_dados.empty:
        return "Município não encontrado", 404
    
    dados = mun_dados.iloc[0].to_dict()
    pos_info = df_municipios[df_municipios['cod_ibge'] == cod_ibge]
    posicao_brasil = pos_info['pos_brasil'].values[0] if not pos_info.empty and 'pos_brasil' in pos_info.columns else '-'
    
    posicao_uf = '-'
    if not pos_info.empty and 'uf' in pos_info.columns:
        uf_atual = pos_info['uf'].values[0]
        df_uf = df_municipios[df_municipios['uf'] == uf_atual].sort_values(by='score_kredita', ascending=False).reset_index(drop=True)
        match = df_uf[df_uf['cod_ibge'] == cod_ibge]
        if not match.empty:
            posicao_uf = int(match.index[0]) + 1

    eixos_selecionados = request.args.getlist('eixos')
    if not eixos_selecionados:
        eixos_selecionados = ['E1', 'E2', 'E3', 'E4']

    num_ativos = len(eixos_selecionados) if eixos_selecionados else 1

    pesos_internos = {
        'I01': ('E1', 'Risco / fragilidade', 0.40),
        'I02': ('E1', 'Risco / fragilidade', 0.25),
        'I03': ('E1', 'Risco / fragilidade', 0.35),
        'I04': ('E2', 'Capacidade financeira', 1/6),
        'I05': ('E2', 'Capacidade financeira', 1/6),
        'I06': ('E2', 'Capacidade financeira', 1/6),
        'I07': ('E2', 'Capacidade financeira', 1/6),
        'I08': ('E2', 'Capacidade financeira', 1/6),
        'I09': ('E2', 'Capacidade financeira', 1/6),
        'I10': ('E3', 'Inclusão', 0.40),
        'I11': ('E3', 'Inclusão', 0.40),
        'I12': ('E3', 'Inclusão', 0.20),
        'I13': ('E4', 'Demografia e acesso', 0.20),
        'I14': ('E4', 'Demografia e acesso', 0.40),
        'I15': ('E4', 'Demografia e acesso', 0.40),
    }

    meta_inds = [
        ('I01', 'I01 · Inadimplência PF (antigo I01)', 'UF ajustada', 'I01', 'S01', '8,83 %'),
        ('I02', 'I02 · Fragilidade de renda', 'Municipal', 'I02', 'S02', '78,04 %'),
        ('I03', 'I03 · Composição dos saldos vencidos 90+', 'UF ajustada', 'I03', 'S03', '61,45 %'),
        ('I04', 'I04 · Desocupação 14+', 'Municipal', 'I04', 'S04', '12,44 %'),
        ('I05', 'I05 · Salário médio de admissão mensal', 'Municipal', 'I05', 'S05', '1.518,00 R$'),
        ('I06', 'I06 · Saldo formal por mil habitantes', 'Municipal', 'I06', 'S06', '0,39 por mil'),
        ('I07', 'I07 · Renda domiciliar per capita', 'Municipal', 'I07', 'S07', '446,05 R$'),
        ('I08', 'I08 · Crédito/depósitos ESTBAN', 'UF ajustada', 'I08', 'S08', '1,56 razão'),
        ('I09', 'I09 · Pix pago por pagador PF', 'Municipal', 'I09', 'S09', '5.681,47 R$'),
        ('I10', 'I10 · Pessoas no CadÚnico por 100 habitantes', 'Municipal', 'I10', 'S10', '40,11'),
        ('I11', 'I11 · Crédito PF per capita', 'UF ajustada', 'I11', 'S11', '13.612,70 R$'),
        ('I12', 'I12 · Informalidade derivada do Censo', 'Municipal', 'I12', 'S12', '49,88 %'),
        ('I13', 'I13 · Variação das estimativas populacionais', 'Municipal', 'I13', 'S13', '0,42 %'),
        ('I14', 'I14 · Participação na força de trabalho 18–64', 'Municipal', 'I14', 'S14', '34,07 %'),
        ('I15', 'I15 · Agências por 100 mil habitantes', 'Municipal', 'I15', 'S16', '0,00'),
    ]

    auditoria_mun = {}
    if not df_auditoria.empty:
        rows_aud = df_auditoria[df_auditoria['cod_ibge'] == cod_ibge]
        for _, r in rows_aud.iterrows():
            ind_key = str(r.get('indicador', '')).upper()
            auditoria_mun[ind_key] = {
                'valor': r.get('valor_ajustado') if pd.notna(r.get('valor_ajustado')) else r.get('valor_bruto'),
                'nota': r.get('nota')
            }

    lista_indicadores = []
    for ind_key, ind_nome, origem, col_val, col_nota, val_fallback in meta_inds:
        eixo_id, nome_eixo, w_interno = pesos_internos[ind_key]
        ativo = eixo_id in eixos_selecionados
        
        if ativo and num_ativos > 0:
            peso_efetivo = w_interno * (1.0 / num_ativos)
        else:
            peso_efetivo = 0.0

        aud_info = auditoria_mun.get(ind_key, {})
        val_usado = aud_info.get('valor') if pd.notna(aud_info.get('valor')) else dados.get(col_val, val_fallback)
        if pd.isna(val_usado):
            val_usado = val_fallback

        raw_nota = aud_info.get('nota') if pd.notna(aud_info.get('nota')) else dados.get(col_nota, 50.0)
        try:
            nota_val = float(raw_nota) if pd.notna(raw_nota) else 50.0
        except (ValueError, TypeError):
            nota_val = 50.0

        contribuicao = nota_val * peso_efetivo if ativo else 0.0

        lista_indicadores.append({
            'nome': ind_nome,
            'eixo': nome_eixo,
            'origem': origem,
            'valor': val_usado,
            'nota': nota_val,
            'peso_percentual': peso_efetivo * 100.0,
            'contribuicao': contribuicao,
            'ativo': ativo
        })

    # Score atual idêntico ao index (média dos eixos E1-E4 selecionados)
    if eixos_selecionados:
        score_atual = float(pd.Series([dados.get(e, 50.0) for e in eixos_selecionados]).mean())
    else:
        score_atual = float(pd.Series([dados.get('E1', 50.0), dados.get('E2', 50.0), dados.get('E3', 50.0), dados.get('E4', 50.0)]).mean())

    # Sem cofator (com valor bruto / notas originais baseado nos eixos ativos)
    info_json = data_json_municipios.get(cod_ibge)
    if info_json:
        mun_json = info_json['json_obj']
        notas_originais = mun_json.get('notas', {}).copy()
        ajustes = mun_json.get('ajustes_estaduais', {})
        for ind, adj in ajustes.items():
            if 'originalNote' in adj:
                notas_originais[ind] = adj['originalNote']
        
        eixos_map = {
            'E1': ['i01', 'i02', 'i03'],
            'E2': ['i04', 'i05', 'i06', 'i07', 'i08', 'i09'],
            'E3': ['i10', 'i11', 'i12'],
            'E4': ['i13', 'i14', 'i15', 'i16']
        }
        
        valores_eixos = []
        for e in eixos_selecionados:
            inds = eixos_map.get(e, [])
            vals = [notas_originais.get(i) for i in inds if notas_originais.get(i) is not None]
            if vals:
                valores_eixos.append(sum(vals) / len(vals))
            else:
                valores_eixos.append(50.0)
        score_sem_cofator = sum(valores_eixos) / len(valores_eixos) if valores_eixos else score_atual
    else:
        score_sem_cofator = score_atual

    dados['score_sem_cofator'] = score_sem_cofator
    dados['score_dinamico'] = score_atual

    return render_template(
        'detalhe.html',
        m=dados,
        indicadores=lista_indicadores,
        pos_brasil=posicao_brasil,
        pos_uf=posicao_uf,
        eixos_ativos=eixos_selecionados
    )

@app.route('/exportar-csv')
def exportar_csv():
    output = io.BytesIO()
    df_municipios.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='ranking_kredita.csv')

if __name__ == '__main__':
    app.run(debug=True)
