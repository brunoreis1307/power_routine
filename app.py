# app.py — Streamlit front: Gerar Plano com acompanhamento de progresso
import streamlit as st
import requests
import time
import uuid
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Power Routine — Gerar Plano", page_icon="⚡", layout="centered")

# ----- Config -----
# Se você tiver a API Flask hospedada, coloque a URL nos secrets ou modifique abaixo.
API_BASE = st.secrets.get("API_BASE", "http://localhost:5000")  # default local

# ----- Inicializar estado -----
if "plans" not in st.session_state:
    st.session_state["plans"] = []  # lista de planos gerados (cada plano é dict)

if "generating" not in st.session_state:
    st.session_state["generating"] = False

if "log" not in st.session_state:
    st.session_state["log"] = []


# ----- Helpers -----
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    st.session_state["log"].append(entry)

def simulate_generate_plan(target_calories: int, days: int, meals_per_day: int, speed=0.03):
    """
    Simula a geração de um plano. Retorna uma lista de items (day, meal_name, food, portion_g).
    A função atualiza logs e progresso (retorna final mealplan dict).
    """
    items = []
    total_steps = days * meals_per_day
    step = 0
    for day in range(1, days + 1):
        for meal_idx in range(1, meals_per_day + 1):
            step += 1
            # Simular trabalho (poderia chamar API aqui)
            time.sleep(speed)  # controle da velocidade da simulação
            # criar item fictício
            item = {
                "day": day,
                "meal_name": f"Refeição {meal_idx}",
                "food_name": f"Alimento ex. {((day-1)*meals_per_day)+meal_idx}",
                "portion_g": 100,
                "done": False
            }
            items.append(item)
            pct = int((step / total_steps) * 100)
            yield {"progress": pct, "current_item": item, "items_so_far": list(items)}
    # final
    yield {"progress": 100, "current_item": None, "items_so_far": list(items)}


def call_api_generate(user_id, target_calories, days, meals_per_day, timeout=25):
    """
    Tenta chamar a API Flask para gerar o plano. Retorna None se falhar.
    Espera que a API POST /api/mealplans aceite payload JSON e retorne generated_items e plan_id.
    """
    url = f"{API_BASE}/api/mealplans"
    payload = {"user_id": user_id, "target_calories": target_calories, "days": days, "meals_per_day": meals_per_day}
    try:
        res = requests.post(url, json=payload, timeout=timeout)
        res.raise_for_status()
        return res.json()  # espera algo como {"plan_id": ..., "generated_items": ...}
    except Exception as e:
        log(f"API generate failed: {e}")
        return None


def save_plan_to_state(plan):
    st.session_state["plans"].insert(0, plan)  # insere no começo


def export_plan_json(plan):
    return json.dumps(plan, ensure_ascii=False, indent=2)


def export_plan_csv(plan):
    # transforma items em DataFrame
    df = pd.DataFrame(plan["items"])
    return df.to_csv(index=False, sep=";")

# ----- UI -----
st.title("Gerar Plano — Power Routine ⚡")
st.caption("Gere um plano alimentar e acompanhe o progresso enquanto ele é criado.")

col1, col2 = st.columns([2, 1])

with col1:
    target_cal = st.number_input("Calorias alvo", min_value=800, max_value=6000, value=2100, step=50)
    days = st.number_input("Dias do plano", min_value=1, max_value=30, value=7)
    meals = st.number_input("Refeições por dia", min_value=1, max_value=6, value=3)
    user_id = st.text_input("User ID (dev)", value="1")
    use_api = st.checkbox("Tentar usar API remota (se disponível)", value=False)

with col2:
    st.write(" ")
    st.write(" ")
    st.write(" ")
    gen_btn = st.button("Gerar Plano Agora", type="primary")

# área de log compacta
with st.expander("Logs / status", expanded=False):
    for entry in st.session_state["log"][-30:]:
        st.write(entry)

# geração do plano
if gen_btn:
    # evitar múltiplas gerações ao mesmo tempo
    if st.session_state["generating"]:
        st.warning("Já existe uma geração em andamento. Aguarde terminar.")
    else:
        st.session_state["generating"] = True
        log(f"Iniciando geração: {target_cal} kcal, {days} dias, {meals} refeição(ões)/dia")
        placeholder = st.empty()
        progress_bar = st.progress(0)
        current_info = st.empty()

        plan_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().isoformat()
        plan = {
            "id": plan_id,
            "user_id": user_id,
            "target_calories": target_cal,
            "days": int(days),
            "meals_per_day": int(meals),
            "created_at": created_at,
            "status": "generating",
            "progress": 0,
            "items": []
        }

        # Tentativa de usar API first (se marcado)
        api_resp = None
        if use_api:
            current_info.info("Tentando gerar via API remota...")
            api_resp = call_api_generate(user_id, target_cal, days, meals)
            if api_resp:
                # se a API retornou plan_id e etc., você pode buscar items via endpoint
                plan["status"] = "generated_via_api"
                plan["progress"] = 100
                plan["items"] = []  # se quiser, buscar /api/mealplans/{id}/items
                # tentar buscar itens
                try:
                    pid = api_resp.get("plan_id") or api_resp.get("id")
                    if pid:
                        r = requests.get(f"{API_BASE}/api/mealplans/{pid}/items", timeout=10)
                        r.raise_for_status()
                        plan["items"] = r.json()
                except Exception as e:
                    log(f"Falha ao buscar itens da API: {e}")
                save_plan_to_state(plan)
                st.session_state["generating"] = False
                st.success("Plano gerado via API com sucesso.")
                st.experimental_rerun()
            else:
                current_info.warning("API indisponível ou falhou — seguindo com geração local.")
                log("API indisponível — fallback para geração local.")

        # Geração local simulada com progresso visual
        generator = simulate_generate_plan(target_cal, int(days), int(meals), speed=0.02)
        try:
            for step in generator:
                pct = step["progress"]
                progress_bar.progress(pct)
                current_item = step["current_item"]
                if current_item:
                    current_info.text(f"Gerando: Dia {current_item['day']} — {current_item['meal_name']} ({pct}%)")
                else:
                    current_info.text("Finalizando...")

                # atualiza plan temporariamente
                plan["progress"] = pct
                plan["items"] = step["items_so_far"]
                # opcional: renderiza lista parcial (compacta)
                with placeholder.container():
                    st.markdown(f"**Progresso:** {pct}% — itens gerados: {len(plan['items'])}")
                    # mostrar 3 últimos itens
                    for it in plan["items"][-3:]:
                        st.write(f"- Dia {it['day']}: {it['meal_name']} — {it['food_name']} ({it['portion_g']} g)")

            # finalizado
            plan["status"] = "generated_local"
            plan["progress"] = 100
            save_plan_to_state(plan)
            st.session_state["generating"] = False
            log(f"Plano {plan_id} gerado localmente com {len(plan['items'])} itens.")
            st.success(f"Plano gerado — ID {plan_id}")
            st.experimental_rerun()
        except Exception as e:
            st.session_state["generating"] = False
            log(f"Erro durante geração: {e}")
            st.error(f"Erro: {e}")

# ----- Mostrar histórico de planos e acompanhamento de progresso -----
st.markdown("---")
st.header("Histórico de Planos")
if not st.session_state["plans"]:
    st.info("Nenhum plano gerado ainda. Gere um plano acima.")
else:
    # Mostrar lista resumida com controles
    for idx, p in enumerate(st.session_state["plans"]):
        with st.expander(f"Plano {p['id']} — {p['target_calories']} kcal — {p['created_at']}", expanded=(idx == 0)):
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**Dias:** {p['days']} • **Ref/dia:** {p['meals_per_day']} • **Status:** {p['status']}")
            # porcentagem calculada a partir dos items 'done'
            total_items = len(p["items"])
            done_items = sum(1 for it in p["items"] if it.get("done"))
            pct_done = int((done_items / total_items) * 100) if total_items else p.get("progress", 0)
            cols[1].metric("Concluído", f"{pct_done}%")
            # botão para exportar e enviar
            if cols[2].button("Exportar JSON", key=f"export_json_{p['id']}"):
                j = export_plan_json(p)
                st.download_button("Download JSON", data=j, file_name=f"plan_{p['id']}.json", mime="application/json")
            # botão para enviar para API (se desejar)
            if cols[2].button("Enviar p/ API", key=f"send_api_{p['id']}"):
                try:
                    r = requests.post(f"{API_BASE}/api/mealplans", json={
                        "user_id": p["user_id"],
                        "target_calories": p["target_calories"],
                        "days": p["days"],
                        "meals_per_day": p["meals_per_day"]
                    }, timeout=10)
                    r.raise_for_status()
                    st.success("Enviado para API.")
                except Exception as e:
                    st.error(f"Falha ao enviar: {e}")

            # tabela de itens com checkbox para marcar conclusão
            if p["items"]:
                # criar cópia para edição
                table_cols = ["day", "meal_name", "food_name", "portion_g", "done"]
                df = pd.DataFrame(p["items"])[table_cols]
                # mostrar tabela editável por checkboxes: vamos renderizar linhas com checkbox
                for i, it in enumerate(p["items"]):
                    cols_row = st.columns([1, 3, 3, 2, 1])
                    cols_row[0].write(it["day"])
                    cols_row[1].write(it["meal_name"])
                    cols_row[2].write(it["food_name"])
                    cols_row[3"].write(f"{it['portion_g']} g")
                    new_done = cols_row[4].checkbox("Concluída", value=it.get("done", False), key=f"{p['id']}_done_{i}")
                    if new_done != it.get("done", False):
                        # atualizar o estado do item
                        p["items"][i]["done"] = new_done
                        log(f"Plano {p['id']} — item dia {it['day']} {'marcado' if new_done else 'desmarcado'}")
                        st.experimental_rerun()

                # botão para marcar todo o plano como concluído
                if st.button("Marcar tudo como concluído", key=f"markall_{p['id']}"):
                    for i in range(len(p["items"])):
                        p["items"][i]["done"] = True
                    st.experimental_rerun()

                # mostrar progresso atualizado
                total_items = len(p["items"])
                done_items = sum(1 for it in p["items"] if it.get("done"))
                pct_done = int((done_items / total_items) * 100) if total_items else 0
                st.progress(pct_done / 100)
                st.write(f"{done_items}/{total_items} itens concluídos — {pct_done}%")

            else:
                st.write("Sem itens listados para este plano.")

# ----- footer / dicas -----
st.markdown("---")
st.caption("Dica: para que o Streamlit possa usar uma API remota, hospede sua API Flask (por exemplo, no Railway ou Render) e configure API_BASE em Secrets do Streamlit.")
