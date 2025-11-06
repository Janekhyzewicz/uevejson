import json
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Editeur de jeux virtuels éducatifs", layout="wide")
st.title("Editeur de jeux virtuels éducatifs UEVE")

# Charger le fichier
uploaded_file = st.file_uploader("Importer un fichier JSON", type="json")

# Si aucun fichier n’est encore chargé, on affiche un message et on arrête là
if not uploaded_file:
    st.info("📂 Importez un fichier JSON pour commencer l’édition.")
    st.stop()

# Lecture sécurisée du fichier
try:
    content = uploaded_file.read().decode("utf-8-sig")
    data = json.loads(content)
except Exception as e:
    st.error(f"Erreur de lecture du fichier JSON : {e}")
    st.stop()

# Vérification du format attendu
if "pages" not in data:
    st.error("❌ Le fichier JSON ne contient pas de clé 'pages'.")
    st.stop()

pages = data["pages"]

# Création des deux colonnes: gauche et droite
col1, col2 = st.columns([1,2])

# Colonne de gauche: éditeur du jeu
with col1:
    st.subheader("Edition")
    page_ids = [page["id"] for page in pages]
    selected_page_id = st.selectbox("Choisir une page", page_ids)

    # Trouver la page active
    page = next(p for p in pages if p["id"] == selected_page_id)

    # Formulaire d'édition
    page["id"] = st.text_input("ID", value=page["id"])
    page["text"] = st.text_area("Texte", value=page["text"], height=150)
    page["backgroundImage"] = st.text_input("Image de fond", value=page.get("backgroundImage", ""))
    page["portraitImage"] = st.text_input("Portrait", value=page.get("portraitImage", ""))

    st.write("### Choix")
    for i, choice in enumerate(page.get("choices", [])):
        choice["id"] = st.text_input(f"ID du choix {i+1}", value=choice["id"], key=f"cid_{page['id']}_{i}")
        choice["text"] = st.text_input(f"Texte du choix {i+1}", value=choice["text"], key=f"ctxt_{page['id']}_{i}")
        choice["nextPage"] = st.text_input(f"Page suivante {i+1}", value=choice["nextPage"], key=f"cnext_{page['id']}_{i}")

    if st.button("Exporter JSON"):
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button("Télécharger le JSON", json_str, file_name="scenario.json", mime="application/json")

# Visualisation du graphe
with col2:
    st.subheader("Visualisation des pages")

    # Construire le graphe avec Pyvis
    net = Network(height="600px", width="100%", directed=True)

    node_ids = {page["id"] for page in pages}
    targets = {choice["nextPage"] for page in pages for choice in page.get("choices", [])}
    end_nodes = node_ids - targets

    for page in pages:
        color = None
        if page["id"] == "p1":
            color = "green"
        elif page["id"] in end_nodes:
            color = "red"

        net.add_node(
            page["id"],
            label=page["id"],
            title=page["text"],
            color=color
        )

    for page in pages:
        for choice in page.get("choices", []):
            target = choice["nextPage"]
            if target not in node_ids:
                net.add_node(target, label=target, color="gray")
                node_ids.add(target)
            net.add_edge(page["id"], target, title=choice["text"], label=choice["text"])

    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=600, scrolling=True)