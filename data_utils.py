import pandas as pd
import streamlit as st
from io import BytesIO

def convert_df_to_csv(df):
    return df.to_csv(index=False, sep=';').encode('utf-8-sig')

def safe_to_numeric(series):
    if series.dtype == 'object':
        series = series.astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
    return pd.to_numeric(series, errors='coerce').fillna(0)

@st.cache_data(ttl=3600)
def carregar_dataframe(arquivo, separador_padrao=','):
    nome_arquivo = arquivo.name.lower()
    if nome_arquivo.endswith('.xlsx'):
        return pd.read_excel(arquivo, engine='openpyxl')
    elif nome_arquivo.endswith('.xls'):
        return pd.read_excel(arquivo, engine='xlrd')
    elif nome_arquivo.endswith('.csv'):
        try:
            arquivo.seek(0)
            df = pd.read_csv(arquivo, encoding='latin-1', sep=separador_padrao, on_bad_lines='skip')
            if len(df.columns) > 1:
                return df
        except Exception:
            pass
        arquivo.seek(0)
        outro_separador = ',' if separador_padrao == ';' else ';'
        df = pd.read_csv(arquivo, encoding='latin-1', sep=outro_separador, on_bad_lines='skip')
        return df
    return None
