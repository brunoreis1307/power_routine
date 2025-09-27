
import streamlit as st
from services.nutri import tmb_mifflin, calorias_alvo, macros_por_objetivo, alertas_dieta

st.markdown("## 🥗 Planejador de Dieta")
st.write("Calcule suas metas calóricas, distribuição de macronutrientes e veja alertas automáticos (RN-016/018/020).")

col1, col2, col3, col4 = st.columns(4)
idade = col1.number_input("Idade", 12, 100, 28)
altura = col2.number_input("Altura (cm)", 50, 250, 170)
peso   = col3.number_input("Peso (kg)", 20.0, 300.0, 70.0)
objetivo = col4.selectbox("Objetivo", ["Cutting", "Bulking", "Manutenção"])

tmb = tmb_mifflin(altura, peso, idade, "M")
kcal_alvo = calorias_alvo(tmb, objetivo)
mac = macros_por_objetivo(kcal_alvo, objetivo)

prot_g = mac["proteina_kcal"] // 4
carb_g = mac["carbo_kcal"] // 4
gord_g = mac["gordura_kcal"] // 9

m1, m2, m3, m4 = st.columns(4)
m1.metric("TMB (estimada)", f"{int(tmb)} kcal")
m2.metric("Calorias alvo", f"{kcal_alvo} kcal")
m3.metric("Carboidratos", f"{carb_g} g/dia", f"{mac['carbo_pct']}%")
m4.metric("Proteínas & Gorduras", f"{prot_g} g / {gord_g} g")

with st.expander("Alertas e recomendações nutricionais"):
    msgs = alertas_dieta(int(tmb), kcal_alvo, mac["carbo_pct"], fibras_pct=28)
    if msgs:
        for m in msgs:
            st.warning(m)
    else:
        st.success("Plano dentro dos parâmetros definidos.")

st.markdown("### Exemplo de plano diário (demonstração)")
st.markdown(
"""
- **Café da manhã:** Ovos mexidos (2), pão integral (1 fatia), fruta (1 porção).  
- **Almoço:** Arroz, feijão, frango grelhado, salada variada.  
- **Lanche:** Iogurte natural + aveia.  
- **Jantar:** Peixe assado + legumes salteados.  
- **Hidratação:** 30–35 ml/kg/dia (ajustar por treino).  
"""
)
st.caption("Observação: Ajuste por preferências/restrições (ex.: vegano, low-carb).")
