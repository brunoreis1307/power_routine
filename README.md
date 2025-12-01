# Power Routine — Módulo Dietas (package)

Este pacote contém um esqueleto de backend em Flask e um front simples em Streamlit para desenvolvimento local.

## Como usar (dev)
1. Criar ambiente virtual e instalar dependências:
   pip install -r requirements.txt
2. Rodar a API Flask:
   python app.py
3. (opcional) Popular DB:
   python data/seed_data.py
4. Rodar o Streamlit:
   streamlit run streamlit_app.py

API base default para o Streamlit é http://localhost:5000 (pode ser configurado via secrets)
