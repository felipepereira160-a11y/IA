import os
import streamlit as st
import google.generativeai as genai

def load_api_key():
    api_key = None
    api_key_status = "Não configurada"
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if api_key:
            api_key_status = "✔️ Carregada (Streamlit Secrets)"
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            api_key_status = "✔️ Carregada (Variável de Ambiente)"
        else:
            api_key_status = "❌ ERRO: Chave não encontrada."
    return api_key, api_key_status

def configure_model(api_key, model_name="gemini-2.5-flash"):
    if not api_key:
        raise ValueError("API key not provided")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar o modelo: {e}")

def mercurio_system_prompt():
    return """Você é Mercúrio, um assistente virtual brasileiro, inteligente, amigável e prestativo.
Fale sempre de forma clara, leve e motivadora, com exemplos práticos quando possível.
Responda perguntas sobre dados usando pandas, Excel, análises financeiras e otimização logística.
Nunca diga que é um modelo de linguagem genérico. Mantenha a personalidade de Mercúrio.
"""
