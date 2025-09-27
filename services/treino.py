
def sugestoes_por_nivel(nivel):
    if nivel == "Iniciante":
        return {"duracao_min": 30, "intensidade": "baixa",
                "exercicios": ["Caminhada rápida (10-15 min)", "Agachamento livre 3x12", "Flexão inclinada 3x10", "Prancha 3x20s"]}
    if nivel == "Intermediário":
        return {"duracao_min": 45, "intensidade": "moderada",
                "exercicios": ["Corrida leve 10 min", "Agachamento 4x10", "Supino 4x8-10", "Remada 4x10", "Prancha 3x40s"]}
    return {"duracao_min": 60, "intensidade": "alta",
            "exercicios": ["HIIT 10x(1' forte / 1' leve)", "Agachamento livre pesado 5x5", "Levantamento terra 5x5", "Barra fixa 4x até falha", "Prancha 3x60s"]}

def variar_grupo_muscular(ultimo_grupo, hoje):
    return hoje if hoje != ultimo_grupo else "Mobilidade/Alongamento (variação automática — RN-019)"

def hidratacao_extra(duracao_min):
    return 500 if duracao_min > 60 else 0  # RN-008
