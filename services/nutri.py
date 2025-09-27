
def tmb_mifflin(altura_cm, peso_kg, idade, sexo="M"):
    if sexo == "M":
        return 10*peso_kg + 6.25*altura_cm - 5*idade + 5
    return 10*peso_kg + 6.25*altura_cm - 5*idade - 161

def calorias_alvo(tmb, objetivo):
    objetivo = objetivo.lower()
    if objetivo == "cutting":
        return int(tmb * 0.85)  # ~15% déficit base
    if objetivo == "bulking":
        return int(tmb * 1.10)  # ~10% superávit
    return int(tmb)

def macros_por_objetivo(calorias, objetivo):
    objetivo = objetivo.lower()
    if objetivo == "cutting":
        p = 0.30; c = 0.40; g = 0.30
    elif objetivo == "bulking":
        p = 0.25; c = 0.50; g = 0.25
    else:
        p = 0.30; c = 0.45; g = 0.25
    return {
        "proteina_kcal": int(calorias*p),
        "carbo_kcal": int(calorias*c),
        "gordura_kcal": int(calorias*g),
        "carbo_pct": int(c*100)
    }

def alertas_dieta(calorias_base, calorias_alvo, carbo_pct, fibras_pct=30):
    msgs = []
    deficit = (calorias_base - calorias_alvo) / max(calorias_base, 1)
    if deficit > 0.30:
        msgs.append("⚠️ Déficit calórico > 30% (RN-020). Risco de estratégia extrema.")
    if carbo_pct > 50:
        msgs.append("⚠️ Carboidratos > 50% das calorias (RN-018). Sugestão: rebalancear com proteínas e gorduras.")
    if fibras_pct < 30:
        msgs.append("⚠️ Baixa ingestão de fibras (< 30% do recomendado) (RN-016).")
    return msgs
