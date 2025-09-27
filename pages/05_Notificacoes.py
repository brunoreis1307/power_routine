
import streamlit as st

st.markdown("## 🔔 Notificações & Insights")
st.write("Alertas automáticos ajudam a manter constância e segurança.")

ultimo_registro = "2025-09-10"
st.write(f"Última atividade registrada: **{ultimo_registro}** (exemplo)")

dias_sem = 17  # simulação
if dias_sem >= 14:
    st.error("Inatividade detectada (≥ 14 dias) — (RN-015). Que tal um treino leve hoje?")
else:
    st.success("Atividade dentro do esperado. Continue assim!")

st.markdown("### Outros insights úteis (demo)")
st.markdown("""
- ✅ Meta de peso com 72% de progresso — mantenha o ritmo.
- 💧 Lembrete: beba água ao longo do dia (30–35 ml/kg). 
- 💤 Sono: tente 7–9 horas/noite para melhor recuperação.
""")
