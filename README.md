# Mercurio

Projeto Streamlit modularizado (Assistente de Dados com IA) — estruturado para rodar no VS Code e versionar no GitHub.

## Como rodar

1. Crie um ambiente virtual (recomendado)
```bash
python -m venv .venv
source .venv/bin/activate   # linux / mac
.venv\Scripts\activate    # windows
```

2. Instale dependências:
```bash
pip install -r requirements.txt
```

3. Execute:
```bash
streamlit run app.py
```

## Estrutura
- `app.py` - ponto de entrada (UI principal)
- `modules/` - módulos organizados: ia_utils, data_utils, analysis_utils, optimizer_utils, dashboard_utils
- `pages/` - páginas alternativas (Modelos, App Básico)
- `requirements.txt` - dependências
- `README.md` - esse arquivo

OBS: Mantenha sua chave `GOOGLE_API_KEY` em `Streamlit Secrets` ou como variável de ambiente para que a IA funcione.
Desenvolvido por Felipe Castro 🚀
