# app.py — Power Routine (Streamlit)
# Pages: Gerar Plano, Educação, Compartilhar Fotos, Feed (photos+articles), Competições, Logs
import streamlit as st
import requests
import time
import uuid
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Power Routine", page_icon="⚡", layout="wide")

# ---------- Config ----------
API_BASE = st.secrets.get("API_BASE", "http://localhost:5000")  # optional remote API

# ---------- Initialize session state ----------
if "plans" not in st.session_state:
    st.session_state["plans"] = []

if "generating" not in st.session_state:
    st.session_state["generating"] = False

if "log" not in st.session_state:
    st.session_state["log"] = []

if "photos" not in st.session_state:
    # photos: list of {id, uploader, caption, image_bytes, created_at, likes, liked_by, group}
    st.session_state["photos"] = []

if "groups" not in st.session_state:
    # groups: name -> {id, members:[], photos:[photo_id], created_at}
    st.session_state["groups"] = {}

if "feed" not in st.session_state:
    # feed: list of {id, type:'photo'|'article', author, created_at, likes, liked_by, data: {...}}
    st.session_state["feed"] = []

if "display_name" not in st.session_state:
    st.session_state["display_name"] = f"User-{str(uuid.uuid4())[:6]}"

# ---------- Helpers ----------
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["log"].append(f"[{ts}] {msg}")

def get_username():
    return st.session_state.get("display_name") or f"User-{str(uuid.uuid4())[:6]}"

def simulate_generate_plan(target_calories: int, days: int, meals_per_day: int, speed=0.02):
    total_steps = days * meals_per_day
    step = 0
    items = []
    for day in range(1, days + 1):
        for meal_idx in range(1, meals_per_day + 1):
            step += 1
            time.sleep(speed)
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
    yield {"progress": 100, "current_item": None, "items_so_far": list(items)}

def save_plan(plan):
    st.session_state["plans"].insert(0, plan)
    log(f"Plano {plan['id']} salvo (local).")

def add_photo(uploader, caption, image_bytes, group_name=None):
    pid = str(uuid.uuid4())[:8]
    photo = {
        "id": pid,
        "uploader": uploader,
        "caption": caption,
        "image_bytes": image_bytes,
        "created_at": datetime.now().isoformat(),
        "likes": 0,
        "liked_by": [],
        "group": group_name
    }
    st.session_state["photos"].insert(0, photo)
    if group_name:
        grp = st.session_state["groups"].get(group_name)
        if grp:
            grp["photos"].insert(0, pid)
    # add to feed
    feed_item = {
        "id": f"p-{pid}",
        "type": "photo",
        "author": uploader,
        "created_at": photo["created_at"],
        "likes": 0,
        "liked_by": [],
        "data": {"photo_id": pid}
    }
    st.session_state["feed"].insert(0, feed_item)
    log(f"Foto {pid} adicionada por {uploader}")
    return pid

def add_article(title, body, author, tags=None):
    aid = str(uuid.uuid4())[:8]
    article = {
        "id": f"a-{aid}",
        "type": "article",
        "author": author,
        "created_at": datetime.now().isoformat(),
        "likes": 0,
        "liked_by": [],
        "data": {"title": title, "body": body, "tags": tags or []}
    }
    st.session_state["feed"].insert(0, article)
    log(f"Artigo '{title}' publicado por {author}")
    return article["id"]

def like_feed_item(feed_id, user):
    # prevent double-like by same user (session-level)
    for item in st.session_state["feed"]:
        if item["id"] == feed_id:
            if user in item.get("liked_by", []):
                return False
            item.setdefault("liked_by", []).append(user)
            item["likes"] = len(item["liked_by"])
            log(f"{user} curtiu {feed_id} (total {item['likes']})")
            # if photo, also update photos list
            if item["type"] == "photo":
                pid = item["data"]["photo_id"]
                for p in st.session_state["photos"]:
                    if p["id"] == pid:
                        p.setdefault("liked_by", []).append(user)
                        p["likes"] = len(p.get("liked_by", []))
                        break
            return True
    return False

def create_group(name, creator):
    if not name or name.strip() == "":
        return False
    if name in st.session_state["groups"]:
        return False
    gid = str(uuid.uuid4())[:6]
    st.session_state["groups"][name] = {"id": gid, "members": [creator], "photos": [], "created_at": datetime.now().isoformat()}
    log(f"Grupo '{name}' criado por {creator}")
    return True

def join_group(name, user):
    grp = st.session_state["groups"].get(name)
    if not grp:
        return False
    if user not in grp["members"]:
        grp["members"].append(user)
        log(f"{user} entrou no grupo '{name}'")
    return True

# ---------- UI: Sidebar ----------
st.sidebar.title("Power Routine")
st.sidebar.markdown("**Identidade (apenas display)**")
disp = st.sidebar.text_input("Seu nome exibido", value=get_username())
st.session_state["display_name"] = disp

page = st.sidebar.selectbox("Navegar", ["Gerar Plano", "Educação", "Compartilhar Fotos", "Feed", "Competições", ])
st.sidebar.markdown("---")


# ---------- PAGE: Gerar Plano ----------
if page == "Gerar Plano":
    st.title("Gerar Plano — Power Routine ⚡")
    st.caption("Gere um plano alimentar e acompanhe o progresso enquanto ele é criado.")
    col1, col2 = st.columns([2, 1])
    with col1:
        target_cal = st.number_input("Calorias alvo", min_value=800, max_value=6000, value=2100, step=50)
        days = st.number_input("Dias do plano", min_value=1, max_value=30, value=7)
        meals = st.number_input("Refeições por dia", min_value=1, max_value=6, value=3)
        user_id = st.text_input("User ID (dev)", value=get_username())

    with col2:
        st.write(" ")
        st.write(" ")
        gen_btn = st.button("Gerar Plano Agora", type="primary")


    if gen_btn:
        if st.session_state["generating"]:
            st.warning("Já existe uma geração em andamento.")
        else:
            st.session_state["generating"] = True
            log(f"Iniciando geração: {target_cal} kcal, {days} dias, {meals} refeição(ões)/dia")
            placeholder = st.empty()
            progress_bar = st.progress(0)
            current_info = st.empty()

            plan_id = str(uuid.uuid4())[:8]
            plan = {
                "id": plan_id,
                "user_id": user_id,
                "target_calories": target_cal,
                "days": int(days),
                "meals_per_day": int(meals),
                "created_at": datetime.now().isoformat(),
                "status": "generating",
                "progress": 0,
                "items": []
            }

            # Try API (if available)
            if use_api:
                try:
                    r = requests.post(f"{API_BASE}/api/mealplans", json={"user_id": user_id, "target_calories": target_cal, "days": days, "meals_per_day": meals}, timeout=10)
                    r.raise_for_status()
                    api_resp = r.json()
                    pid = api_resp.get("plan_id") or api_resp.get("id")
                    plan["status"] = "generated_via_api"
                    plan["progress"] = 100
                    if pid:
                        try:
                            r2 = requests.get(f"{API_BASE}/api/mealplans/{pid}/items", timeout=10)
                            r2.raise_for_status()
                            plan["items"] = r2.json()
                        except Exception as e:
                            log(f"Falha ao buscar itens da API: {e}")
                    save_plan(plan)
                    st.session_state["generating"] = False
                    st.success("Plano gerado via API.")
                    st.experimental_rerun()
                except Exception as e:
                    log(f"API generate failed: {e}")
                    st.warning("API indisponível — gerando localmente.")

            # local generation
            try:
                generator = simulate_generate_plan(target_cal, int(days), int(meals), speed=0.02)
                for step in generator:
                    pct = step["progress"]
                    progress_bar.progress(pct)
                    current_item = step["current_item"]
                    if current_item:
                        current_info.text(f"Gerando: Dia {current_item['day']} — {current_item['meal_name']} ({pct}%)")
                    else:
                        current_info.text("Finalizando...")

                    plan["progress"] = pct
                    plan["items"] = step["items_so_far"]
                    with placeholder.container():
                        st.markdown(f"**Progresso:** {pct}% — itens gerados: {len(plan['items'])}")
                        for it in plan["items"][-3:]:
                            st.write(f"- Dia {it['day']}: {it['meal_name']} — {it['food_name']} ({it['portion_g']} g)")
                plan["status"] = "generated_local"
                plan["progress"] = 100
                save_plan(plan)
                st.session_state["generating"] = False
                log(f"Plano {plan_id} gerado localmente.")
                st.success(f"Plano gerado — ID {plan_id}")
                st.experimental_rerun()
            except Exception as e:
                st.session_state["generating"] = False
                log(f"Erro durante geração: {e}")
                st.error(f"Erro: {e}")

    st.markdown("---")
    st.header("Histórico de Planos")
    if not st.session_state["plans"]:
        st.info("Nenhum plano gerado ainda.")
    else:
        for idx, p in enumerate(st.session_state["plans"]):
            with st.expander(f"Plano {p['id']} — {p['target_calories']} kcal — {p['created_at']}", expanded=(idx==0)):
                cols = st.columns([3,1,1])
                cols[0].write(f"**Dias:** {p['days']} • **Ref/dia:** {p['meals_per_day']} • **Status:** {p['status']}")
                total_items = len(p["items"])
                done_items = sum(1 for it in p["items"] if it.get("done"))
                pct_done = int((done_items / total_items) * 100) if total_items else p.get("progress",0)
                cols[1].metric("Concluído", f"{pct_done}%")
                if cols[2].button("Exportar JSON", key=f"export_json_{p['id']}"):
                    j = json.dumps(p, ensure_ascii=False, indent=2)
                    st.download_button("Download JSON", data=j, file_name=f"plan_{p['id']}.json", mime="application/json")
                if p["items"]:
                    for i, it in enumerate(p["items"]):
                        cols_row = st.columns([1,3,3,2,1])
                        cols_row[0].write(it["day"])
                        cols_row[1].write(it["meal_name"])
                        cols_row[2].write(it["food_name"])
                        cols_row[3].write(f"{it['portion_g']} g")
                        new_done = cols_row[4].checkbox("Concluída", value=it.get("done", False), key=f"{p['id']}_done_{i}")
                        if new_done != it.get("done", False):
                            p["items"][i]["done"] = new_done
                            log(f"Plano {p['id']} — item dia {it['day']} {'marcado' if new_done else 'desmarcado'}")
                            st.experimental_rerun()
                    if st.button("Marcar tudo como concluído", key=f"markall_{p['id']}"):
                        for i in range(len(p["items"])):
                            p["items"][i]["done"] = True
                        st.experimental_rerun()
                    total_items = len(p["items"])
                    done_items = sum(1 for it in p["items"] if it.get("done"))
                    pct_done = int((done_items / total_items) * 100) if total_items else 0
                    st.progress(pct_done / 100)
                    st.write(f"{done_items}/{total_items} itens concluídos — {pct_done}%")

# ---------- PAGE: Educação ----------
elif page == "Educação":
    st.title("Educação — Dietas & Treinos")
    st.markdown("Conteúdos educativos curtos e práticos sobre nutrição, treino e hábitos saudáveis.")
    articles = [
        {"title": "Princípios básicos de uma dieta equilibrada",
         "body": "**Macronutrientes:** carboidratos (energia), proteínas (recuperação/massa) e gorduras (hormônios, absorção).  \n**Hidratação:** beba água ao longo do dia.  \n**Frequência:** 3–6 refeições/dia conforme preferência.  \n**Dica prática:** Priorize alimentos integrais e controle o tamanho das porções."},
        {"title": "Como estruturar um treino para hipertrofia",
         "body": "**Frequência:** 3–5 sessões/semana.  \n**Volume:** 8–20 séries por grupo muscular por semana.  \n**Progressão:** aumente carga ou repetições gradualmente.  \n**Recuperação:** durma bem e garanta ingestão proteica adequada."},
        {"title": "Recuperação e sono",
         "body": "O sono é crucial para recuperação muscular e regulação hormonal. Rotina fixa, evitar telas 1h antes e garantir 7–9h de sono."}
    ]
    for a in articles:
        st.subheader(a["title"])
        st.markdown(a["body"])
        st.markdown("---")

# ---------- PAGE: Compartilhar Fotos ----------
elif page == "Compartilhar Fotos":
    st.title("Compartilhar Fotos de Treino")
    st.write("Compartilhe imagens dos seus treinos, inspire outras pessoas e acompanhe progresso visual.")
    uploader_col, gallery_col = st.columns([1,2])

    with uploader_col:
        st.subheader("Novo envio")
        caption = st.text_input("Legenda (ex.: Squat 3x10)", value="")
        choose_group = st.selectbox("Postar em grupo (opcional)", options=[""] + list(st.session_state["groups"].keys()))
        img_file = st.file_uploader("Selecione imagem (jpg/png)", type=["png","jpg","jpeg"])
        if st.button("Enviar foto"):
            if not img_file:
                st.error("Envie uma imagem antes.")
            else:
                try:
                    img_bytes = img_file.read()
                    pid = add_photo(get_username(), caption, img_bytes, group_name=(choose_group or None))
                    st.success(f"Foto enviada (id {pid})")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Falha ao enviar: {e}")

        st.markdown("---")
        st.subheader("Publicar artigo (blog)")
        a_title = st.text_input("Título do artigo", value="")
        a_body = st.text_area("Corpo do artigo (markdown suportado)", value="")
        if st.button("Publicar artigo"):
            if not a_title.strip() or not a_body.strip():
                st.error("Título e corpo são necessários.")
            else:
                aid = add_article(a_title.strip(), a_body.strip(), get_username())
                st.success(f"Artigo publicado (id {aid})")
                st.experimental_rerun()

    with gallery_col:
        st.subheader("Galeria")
        photos = st.session_state["photos"]
        if not photos:
            st.info("Nenhuma foto enviada ainda.")
        else:
            cols = st.columns(3)
            for i, p in enumerate(photos):
                col = cols[i % 3]
                try:
                    col.image(p["image_bytes"], caption=f"{p['caption']} — por {p['uploader']}", use_column_width=True)
                except Exception:
                    col.write(f"{p['caption']} — por {p['uploader']}")
                col.write(f"Grupo: {p['group'] or '—'} • Likes: {p['likes']}")
                if col.button("Curtir ❤️", key=f"like_{p['id']}"):
                    # simple like: update both photo and feed item (prevent dup by session)
                    liked = False
                    # find feed item
                    feed_id = f"p-{p['id']}"
                    if like_feed_item(feed_id, get_username()):
                        liked = True
                    if liked:
                        st.success("Você curtiu esta foto.")
                    else:
                        st.warning("Você já curtiu esta foto.")
                    st.experimental_rerun()

# ---------- PAGE: Feed ----------
elif page == "Feed":
    st.title("Feed — Comunidade")
    st.write("Fotos e artigos publicados pela comunidade.")
    left, right = st.columns([2,1])

    with left:
        st.subheader("Filtros")
        group_opts = ["Todos"] + list(st.session_state["groups"].keys())
        sel_group = st.selectbox("Filtrar por grupo", options=group_opts, index=0)
        sel_type = st.selectbox("Tipo", options=["Todos", "Fotos", "Artigos"], index=0)
        order = st.selectbox("Ordenar por", options=["Mais recentes", "Mais curtidas"], index=0)

        # build feed list
        feed_items = []
        for item in st.session_state["feed"]:
            if sel_type == "Fotos" and item["type"] != "photo":
                continue
            if sel_type == "Artigos" and item["type"] != "article":
                continue
            if sel_group != "Todos":
                if item["type"] == "photo":
                    pid = item["data"]["photo_id"]
                    photo = next((p for p in st.session_state["photos"] if p["id"]==pid), None)
                    if not photo or photo.get("group") != sel_group:
                        continue
                else:
                    # articles don't have group in this model; skip filtering articles by group
                    continue
            feed_items.append(item)

        if order == "Mais curtidas":
            feed_items = sorted(feed_items, key=lambda x: x.get("likes",0), reverse=True)
        else:
            feed_items = sorted(feed_items, key=lambda x: x.get("created_at",""), reverse=True)

        if not feed_items:
            st.info("Nenhum item encontrado.")
        else:
            for it in feed_items:
                if it["type"] == "photo":
                    pid = it["data"]["photo_id"]
                    photo = next((p for p in st.session_state["photos"] if p["id"]==pid), None)
                    if not photo:
                        continue
                    st.image(photo["image_bytes"], use_column_width=True, caption=f"{photo['caption']}")
                    st.write(f"Por: {it['author']} • Grupo: {photo.get('group') or '—'} • {it['created_at'][:19]}")
                    cols = st.columns([1,4,1])
                    cols[1].write(f"Curtidas: {it.get('likes',0)}")
                    if cols[2].button("Curtir ❤️", key=f"feed_like_{it['id']}"):
                        ok = like_feed_item(it['id'], get_username())
                        if ok:
                            st.success("Curtiu!")
                        else:
                            st.warning("Você já curtiu.")
                        st.experimental_rerun()
                    st.markdown("---")
                else:  # article
                    st.subheader(it["data"]["title"])
                    st.write(f"Por: {it['author']} • {it['created_at'][:19]}")
                    st.markdown(it["data"]["body"])
                    cols = st.columns([1,4,1])
                    cols[1].write(f"Curtidas: {it.get('likes',0)}")
                    if cols[2].button("Curtir artigo ❤️", key=f"feed_like_{it['id']}"):
                        ok = like_feed_item(it['id'], get_username())
                        if ok:
                            st.success("Você curtiu o artigo.")
                        else:
                            st.warning("Você já curtiu.")
                        st.experimental_rerun()
                    st.markdown("---")

    with right:
        st.subheader("Atalhos")
        if st.button("Ver minhas fotos"):
            # show only user's photos
            my_photos = [p for p in st.session_state["photos"] if p["uploader"]==get_username()]
            if not my_photos:
                st.info("Você ainda não enviou fotos.")
            else:
                for p in my_photos:
                    st.image(p["image_bytes"], use_column_width=True, caption=p["caption"])
                    st.write(f"Curtidas: {p.get('likes',0)} • Grupo: {p.get('group') or '—'}")

# ---------- PAGE: Competições ----------
elif page == "Competições":
    st.title("Competições entre Grupos")
    st.write("Crie grupos, junte membros, poste fotos no grupo e compita com seus amigos.")
    left, right = st.columns([1,2])

    with left:
        st.subheader("Criar / Entrar")
        new_group = st.text_input("Nome do novo grupo", value="")
        if st.button("Criar grupo"):
            if create_group(new_group.strip(), get_username()):
                st.success(f"Grupo '{new_group}' criado.")
            else:
                st.error("Falha ao criar (nome inválido ou já existe).")
        join_name = st.selectbox("Entrar em grupo", options=[""] + list(st.session_state["groups"].keys()))
        if st.button("Entrar no grupo"):
            if join_name:
                join_group(join_name, get_username())
                st.success(f"Você entrou no grupo '{join_name}'")
            else:
                st.error("Escolha um grupo.")

    with right:
        st.subheader("Ranking")
        leaderboard = []
        for gname, g in st.session_state["groups"].items():
            total_likes = sum(next((p["likes"] for p in st.session_state["photos"] if p["id"]==pid), 0) for pid in g["photos"])
            leaderboard.append({"group": gname, "likes": total_likes, "members": len(g["members"]), "photos": len(g["photos"])})
        if leaderboard:
            df = pd.DataFrame(sorted(leaderboard, key=lambda x: x["likes"], reverse=True))
            st.table(df)
        else:
            st.info("Ainda não há competições ativas.")

