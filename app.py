
import streamlit as st

st.set_page_config(page_title="Power Routine", page_icon="💪", layout="wide")

# Estilos simples (cores fixas para evitar conflito de formatação)
st.markdown("""
<style>
    .stApp { background-color: #000000; color: white; }
    .pr-title { font-size: 30px; font-weight: 800; color: #16FF00; }
    .pr-card { background: #0b0b0b; padding: 16px; border-radius: 16px; }
    .muted { opacity: .85; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## Navegação")
st.sidebar.page_link("app.py", label="🏠 Início")
st.sidebar.page_link("pages/01_Perfil.py", label="👤 Perfil")
st.sidebar.page_link("pages/02_Dieta.py", label="🥗 Dieta")
st.sidebar.page_link("pages/03_Treinos.py", label="🏋️ Treinos")
st.sidebar.page_link("pages/04_Progresso.py", label="📈 Progresso")
st.sidebar.page_link("pages/05_Notificacoes.py", label="🔔 Notificações")

st.markdown('<div class="pr-title">Power Routine — Painel Funcional</div>', unsafe_allow_html=True)
st.write("Bem-vindo! Este é o MVP do aplicativo PR (Power Routine). Use o menu ao lado para navegar pelas áreas.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Usuários ativos (demo)", "1.284", "+8%")
with col2:
    st.metric("Dietas validadas (demo)", "742", "+3%")
with col3:
    st.metric("Treinos concluídos (demo)", "5.963", "+12%")

st.markdown("### Como usar")
st.markdown(
    '<div class="pr-card muted">'
    "1) Preencha seus dados em <b>Perfil</b> • "
    "2) Calcule metas e veja alertas em <b>Dieta</b> • "
    "3) Veja sugestões e segurança em <b>Treinos</b> • "
    "4) Acompanhe gráficos em <b>Progresso</b> • "
    "5) Verifique <b>Notificações</b> como inatividade e lembretes."
    "</div>",
    unsafe_allow_html=True
)
