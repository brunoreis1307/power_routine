import streamlit as st
import requests

st.set_page_config(page_title="Power Routine", page_icon="⚡", layout="centered")

st.title("Power Routine ⚡ — Módulo Dietas")

st.sidebar.header("Menu")
page = st.sidebar.selectbox("Navegar", ["Home","Gerar Plano","Lista de Compras","Seed DB (dev)"])

API_BASE = st.secrets.get("API_BASE","http://localhost:5000")

if page == "Home":
    st.subheader("Bem-vindo ao Power Routine")
    st.write("Use o menu para gerar planos ou ver a lista de compras.")

if page == "Gerar Plano":
    cal = st.number_input("Calorias alvo", min_value=1200, max_value=4000, value=2100)
    days = st.number_input("Dias do plano", min_value=1, max_value=30, value=7)
    meals = st.number_input("Refeições por dia", min_value=1, max_value=6, value=3)
    user_id = st.text_input("User ID (dev)", value="1")
    if st.button("Gerar plano (via API)"):
        payload = {"user_id": user_id, "target_calories": cal, "days": days, "meals_per_day": meals}
        try:
            res = requests.post(f"{API_BASE}/api/mealplans", json=payload, timeout=10)
            st.write(res.json())
        except Exception as e:
            st.error(f"Erro ao chamar API: {e}")

if page == "Lista de Compras":
    plan_id = st.text_input("Plan ID", value="")
    if st.button("Gerar lista (via API)"):
        try:
            res = requests.get(f"{API_BASE}/api/mealplans/{plan_id}/shopping_list", timeout=10)
            st.write(res.json())
        except Exception as e:
            st.error(f"Erro ao chamar API: {e}")

if page == "Seed DB (dev)":
    if st.button("Executar seed (via API)"):
        st.info("Execute data/seed_data.py localmente no servidor Flask para popular o banco.")
