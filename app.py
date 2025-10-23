import streamlit as st
from modules.ia_utils import load_api_key, configure_model, mercurio_system_prompt
from modules.data_utils import carregar_dataframe, convert_df_to_csv
from modules.dashboard_utils import show_basic_dashboard
from modules.optimizer_utils import suggest_rt_for_city
from modules.analysis_utils import analisar_custos_duplicidade
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="🧠 Mercúrio IA", page_icon="🧠", layout="wide")
st.title("🧠 Mercúrio IA")
st.caption("Desenvolvido por Felipe Castro 🚀")

api_key, api_status = load_api_key()
st.sidebar.caption(f"**Status da Chave de API:** {api_status}")
if not api_key:
    st.error("A chave da API do Google não foi encontrada. O aplicativo não pode funcionar.")
    st.stop()

# Initialize model lazily when needed
_model = None
def get_model():
    global _model
    if _model is None:
        try:
            _model = configure_model(api_key)
        except Exception as e:
            st.error(f"Erro ao iniciar IA: {e}")
            st.stop()
    return _model

# Session-state safe dataframes
for key in ['df_dados', 'df_mapeamento', 'df_devolucao', 'df_pagamento']:
    if key not in st.session_state:
        st.session_state[key] = None

with st.sidebar:
    st.header("Base de Conhecimento")
    tipos_permitidos = ["csv","xlsx","xls"]
    data_file = st.file_uploader("1. 📊 Upload Pesquisa de O.S (OS)", type=tipos_permitidos)
    if data_file:
        try:
            st.session_state.df_dados = carregar_dataframe(data_file, separador_padrao=';')
            st.success("Agendamentos carregados!")
        except Exception as e:
            st.error(f"Erro nos dados: {e}")

    st.markdown("---")
    map_file = st.file_uploader("2. 🌍 Upload do Mapeamento de RT (Fixo)", type=tipos_permitidos)
    if map_file:
        try:
            st.session_state.df_mapeamento = carregar_dataframe(map_file, separador_padrao=',')
            st.success("Mapeamento carregado!")
        except Exception as e:
            st.error(f"Erro no mapeamento: {e}")

    st.markdown("---")
    devolucao_file = st.file_uploader("3. 📥 Upload de Itens a Instalar (Devolução)", type=tipos_permitidos)
    if devolucao_file:
        try:
            st.session_state.df_devolucao = carregar_dataframe(devolucao_file, separador_padrao=';')
            st.success("Base de devolução carregada!")
        except Exception as e:
            st.error(f"Erro na base de devolução: {e}")

    st.markdown("---")
    pagamento_file = st.file_uploader("4. 💵 Upload da Base de Pagamento (Duplicidade)", type=tipos_permitidos)
    if pagamento_file:
        try:
            st.session_state.df_pagamento = carregar_dataframe(pagamento_file, separador_padrao=';')
            st.success("Base de pagamento carregada!")
        except Exception as e:
            st.error(f"Erro na base de pagamento: {e}")

    if st.button("Limpar Tudo"):
        st.session_state.clear()
        st.rerun()

# Main body
st.markdown("---")
if st.session_state.df_dados is not None:
    show_basic_dashboard(st.session_state.df_dados)

if st.session_state.df_mapeamento is not None:
    st.markdown("---")
    st.header("🗺️ Ferramenta de Mapeamento e Consulta de RT")
    df_map = st.session_state.df_mapeamento.copy()
    required = ['nm_cidade_atendimento','nm_representante','cd_latitude_atendimento','cd_longitude_atendimento','qt_distancia_atendimento_km']
    if all(c in df_map.columns for c in required):
        cidade = st.selectbox("Filtrar Mapeamento por Cidade:", options=sorted(df_map['nm_cidade_atendimento'].dropna().unique()))
        rep = st.selectbox("Filtrar Mapeamento por Representante:", options=sorted(df_map['nm_representante'].dropna().unique()))
        filtered = df_map
        if cidade:
            filtered = df_map[df_map['nm_cidade_atendimento']==cidade]
        elif rep:
            filtered = df_map[df_map['nm_representante']==rep]
        st.dataframe(filtered)
        st.write("Visualização no Mapa:")
        map_data = filtered.rename(columns={'cd_latitude_atendimento':'lat','cd_longitude_atendimento':'lon'})
        map_data['lat'] = pd.to_numeric(map_data['lat'], errors='coerce')
        map_data['lon'] = pd.to_numeric(map_data['lon'], errors='coerce')
        map_data.dropna(subset=['lat','lon'], inplace=True)
        if not map_data.empty:
            map_data['size']=1000
            st.map(map_data)
        else:
            st.warning("Nenhum resultado com coordenadas para exibir no mapa.")

if st.session_state.df_pagamento is not None:
    st.markdown("---")
    st.header("🔎 Analisador de Custos e Duplicidade de Deslocamento")
    try:
        resultado = analisar_custos_duplicidade(st.session_state.df_pagamento)
        if resultado.empty:
            st.success("Nenhuma duplicidade encontrada ou nenhum dado com custos positivos.")
        else:
            st.dataframe(resultado)
            csv = convert_df_to_csv(resultado)
            st.download_button("📥 Exportar Resultado (.csv)", data=csv, file_name="analise_duplicidade.csv", mime='text/csv')
    except Exception as e:
        st.error(f"Erro na análise: {e}")

if st.session_state.df_dados is not None and st.session_state.df_mapeamento is not None:
    st.markdown("---")
    st.header("🚚 Otimizador de Proximidade de RT")
    cidade_para_otim = st.selectbox("Selecione uma cidade para otimizar:", options=sorted(st.session_state.df_dados.iloc[:,0].dropna().unique()) if st.session_state.df_dados is not None else [])
    if cidade_para_otim:
        try:
            df_dist = suggest_rt_for_city(st.session_state.df_mapeamento, cidade_para_otim)
            if df_dist.empty:
                st.warning("Nenhum representante sugerido para essa cidade.")
            else:
                st.dataframe(df_dist.sort_values('Distancia (km)').head(10))
        except Exception as e:
            st.error(f"Erro no otimizador: {e}")

# Simple chat (lightweight) - sends prompt to Gemini when user asks general questions
st.markdown("---")
st.header("💬 Converse com a IA (Mercúrio)")
for message in st.session_state.get('display_history', []):
    with st.chat_message(message['role']):
        st.markdown(message['content'])

prompt = st.chat_input("Envie uma pergunta ou mensagem...")
if prompt:
    st.session_state.setdefault('display_history', []).append({'role':'user','content':prompt})
    model = get_model()
    system = mercurio_system_prompt()
    full_prompt = system + "\n\nPergunta do usuário: " + prompt
    try:
        response = model.generate_content(full_prompt)
        resposta = response.text.strip()
    except Exception as e:
        resposta = f"Erro ao gerar resposta: {e}"
    st.session_state['display_history'].append({'role':'assistant','content':resposta})
    with st.chat_message('assistant'):
        st.markdown(resposta)
