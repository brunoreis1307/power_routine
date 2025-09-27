
import streamlit as st
import pandas as pd

st.markdown("## 📈 Evolução & Metas")
st.write("Acompanhe a evolução de peso e treinos concluídos. Ao atingir 100% da meta, sugerimos definir uma nova (RN-010).")

# Mock de dados
df = pd.DataFrame({
    "dia": pd.date_range("2025-08-01", periods=30, freq="D"),
    "peso": [75 - i*0.1 for i in range(30)],
    "treinos": [1 if i%2==0 else 0 for i in range(30)]
})

c1, c2 = st.columns(2)
with c1:
    st.line_chart(df.set_index("dia")["peso"], height=260)
with c2:
    st.bar_chart(df.set_index("dia")["treinos"], height=260)

meta_inicial = 75
meta_alvo = 70
meta_atual = df["peso"].iloc[-1]
pct_meta = (meta_inicial - meta_atual) / max((meta_inicial - meta_alvo), 0.0001)
st.metric("Meta de peso", f"{meta_atual:.1f} kg", f"{pct_meta*100:.1f}% de progresso")

if pct_meta >= 1.0:
    st.success("Meta atingida! Sugestão: iniciar fase de **manutenção** ou **definição** (RN-010).")
else:
    st.info("Dica: mantenha constância e registre treinos/refeições para acelerar o progresso.")
