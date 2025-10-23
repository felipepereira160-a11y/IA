import streamlit as st
import pandas as pd

def find_column(df, keywords):
    for c in df.columns:
        for k in keywords:
            if k in c.lower():
                return c
    return None

def show_basic_dashboard(df):
    st.header("📊 Dashboard de Análise de Ordens de Serviço")
    df_analise = df.copy()
    status_col = find_column(df_analise, ['status'])
    rep_col_dados = find_column(df_analise, ['representante técnico', 'representante'])
    city_col_dados = find_column(df_analise, ['cidade agendamento', 'cidade o.s.'])
    motivo_fechamento_col = find_column(df_analise, ['tipo de fechamento', 'tipo de fechamento'])

    st.subheader("Análises Gráficas")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Ordens Agendadas por Cidade (Top 10)**")
        if status_col and city_col_dados:
            agendadas_df = df_analise[df_analise[status_col] == 'Agendada']
            st.bar_chart(agendadas_df[city_col_dados].value_counts().nlargest(10))
        else:
            st.warning("Colunas 'Status' ou 'Cidade Agendamento' não encontradas.")
    with col2:
        st.write("**Total de Ordens por RT (Top 10)**")
        if rep_col_dados:
            st.bar_chart(df_analise[rep_col_dados].value_counts().nlargest(10))
        else:
            st.warning("Coluna 'Representante Técnico' não encontrada.")
