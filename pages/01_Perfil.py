
import streamlit as st

st.markdown("## 👤 Perfil do Usuário")
st.write("Preencha seus dados para personalizar recomendações de treino e dieta.")

with st.form("perfil"):
    col1, col2, col3 = st.columns(3)
    with col1:
        idade = st.number_input("Idade (anos)", min_value=12, max_value=100, value=28)
        altura = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170)
    with col2:
        peso = st.number_input("Peso (kg)", min_value=20.0, max_value=300.0, value=70.0)
        nivel = st.selectbox("Nível de atividade", ["Iniciante", "Intermediário", "Avançado"])
    with col3:
        objetivo = st.selectbox("Objetivo", ["Cutting", "Bulking", "Manutenção"])
        problemas = st.multiselect("Condições de saúde", ["Nenhum", "Diabetes", "Hipertensão", "Problemas cardíacos", "Outros"])

    submitted = st.form_submit_button("Salvar perfil")
    if submitted:
        st.success("Perfil salvo (exemplo). Recomendações personalizadas ativadas (RN-006).")
        if "Nenhum" not in problemas and len(problemas) > 0:
            st.warning("Com base nos dados de saúde, treinos intensos serão limitados (RN-007).")
st.info("Dica: Você pode alterar o objetivo a qualquer momento. Peso/altura devem ser atualizados com parcimônia (regra de negócio).")
