import pandas as pd
import numpy as np
from .data_utils import safe_to_numeric

def analisar_custos_duplicidade(df_pagamento):
    # Espera colunas específicas; faz validações e retorna DataFrame pronto p/ exibição
    df_custos = df_pagamento.copy()
    # Detectar colunas com heurística (retorna None se faltar)
    def find_col(cols, keywords):
        for k in cols:
            if any(keyword in k.lower() for keyword in keywords):
                return k
        return None

    cols = df_custos.columns.tolist()
    os_col = find_col(cols, ['os'])
    data_fech_col = find_col(cols, ['data de fechamento', 'data fechamento', 'data_fechamento'])
    cidade_os_col = find_col(cols, ['cidade o.s.', 'cidade os', 'cidade agendamento'])
    cidade_rt_col = find_col(cols, ['cidade rt'])
    rep_col = find_col(cols, ['representante'])
    tec_col = find_col(cols, ['técnico', 'tecnico'])
    valor_desl_col = find_col(cols, ['valor deslocamento'])
    desloc_km_col = find_col(cols, ['deslocamento'])
    valor_km_col = find_col(cols, ['valor km'])
    abrang_col = find_col(cols, ['abrangência', 'ac abrangência', 'ac abrangencia'])
    valor_extra_col = find_col(cols, ['valor extra'])
    pedagio_col = find_col(cols, ['pedágio', 'pedagio'])

    required_cols = [os_col, data_fech_col, cidade_os_col, cidade_rt_col, rep_col, tec_col, valor_desl_col, desloc_km_col, valor_km_col, abrang_col, valor_extra_col, pedagio_col]
    if not all(required_cols):
        raise ValueError("Planilha de pagamento não contém todas as colunas necessárias para análise.")

    df_custos['VALOR_DESLOC_ORIGINAL'] = safe_to_numeric(df_custos[valor_desl_col])
    df_custos['VALOR_EXTRA_NUM'] = safe_to_numeric(df_custos[valor_extra_col])
    df_custos['PEDAGIO_NUM'] = safe_to_numeric(df_custos[pedagio_col])
    filtro_custos_positivos_mask = ((df_custos['VALOR_DESLOC_ORIGINAL'] > 0) | (df_custos['VALOR_EXTRA_NUM'] > 0) | (df_custos['PEDAGIO_NUM'] > 0))
    df_custos = df_custos[filtro_custos_positivos_mask].copy()
    if df_custos.empty:
        return pd.DataFrame()  # sinaliza vazio

    df_custos['DATA_ANALISE'] = pd.to_datetime(df_custos[data_fech_col], dayfirst=True, errors='coerce').dt.date

    df_custos['DESLOC_KM_NUM'] = safe_to_numeric(df_custos[desloc_km_col])
    df_custos['VALOR_KM_NUM'] = safe_to_numeric(df_custos[valor_km_col])
    df_custos['ABRANG_NUM'] = safe_to_numeric(df_custos[abrang_col])
    mesma_cidade_mask = df_custos[cidade_rt_col] == df_custos[cidade_os_col]
    valor_calculado = (df_custos['DESLOC_KM_NUM'] * df_custos['VALOR_KM_NUM']) - df_custos['ABRANG_NUM']
    valor_calculado[valor_calculado < 0] = 0
    df_custos['VALOR_CALCULADO'] = np.where(mesma_cidade_mask, 0, valor_calculado)
    df_custos['OBSERVACAO'] = np.where(mesma_cidade_mask, "Custo Zerado (Mesma Cidade)", "")

    # Duplicidade
    group_keys = ['DATA_ANALISE', cidade_os_col, rep_col, tec_col]
    df_custos['is_first'] = ~df_custos.duplicated(subset=group_keys, keep='first')
    grupos_com_duplicatas = df_custos.groupby(group_keys).filter(lambda x: len(x) > 1)
    if grupos_com_duplicatas.empty:
        return pd.DataFrame()
    grupos_com_duplicatas['VALOR_CALCULADO_AJUSTADO'] = np.where(grupos_com_duplicatas['is_first'], grupos_com_duplicatas['VALOR_CALCULADO'], 0)
    grupos_com_duplicatas['OBSERVACAO'] = np.where(grupos_com_duplicatas['is_first'], grupos_com_duplicatas['OBSERVACAO'], "Duplicidade (Custo Zerado)")
    return grupos_com_duplicatas
