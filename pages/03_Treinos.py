
import streamlit as st
from services.treino import sugestoes_por_nivel, variar_grupo_muscular, hidratacao_extra

st.markdown("## 🏋️ Treinos do Dia")
st.write("Sugestões de treino por nível, variação para evitar sobrecarga (RN-019) e orientação de hidratação (RN-008).")

nivel = st.selectbox("Nível", ["Iniciante", "Intermediário", "Avançado"])
grupo_ontem = st.selectbox("Grupo muscular de ontem", ["Pernas", "Peito", "Costas", "Ombros", "Mobilidade/Alongamento"])
grupo_hoje = st.selectbox("Grupo desejado hoje", ["Pernas", "Peito", "Costas", "Ombros", "Mobilidade/Alongamento"])

sug = sugestoes_por_nivel(nivel)
grupo_final = variar_grupo_muscular(grupo_ontem, grupo_hoje)
agua = hidratacao_extra(sug["duracao_min"])

st.write(f"**Intensidade:** {sug['intensidade']} • **Duração:** {sug['duracao_min']} min • **Grupo recomendado:** {grupo_final}")
st.write("**Exercícios sugeridos:**")
st.write("- " + "\n- ".join(sug["exercicios"]))

if agua > 0:
    st.info(f"Sugestão de hidratação extra: {agua} ml (para treinos > 60 min).")

if grupo_final != grupo_hoje:
    st.warning("Variação automática aplicada para evitar trabalhar o mesmo grupo em dias consecutivos (RN-019).")

st.caption("Atenção: ajuste cargas e volume conforme evolução e histórico de lesões.")
