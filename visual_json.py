import json
import streamlit as st
import io
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Éditeur de scénario", layout="wide")

st.title("📖 Éditeur de scénario interactif")

# --- Charger le JSON ---
uploaded_file = st.file_uploader("Importer un fichier JSON", type="json")
if uploaded_file:
    # uploaded_file est un flux binaire -> il faut lire et décoder
    content = uploaded_file.read().decode("utf-8-sig")

    # controle qualité du fichier    
    st.text_area("Contenu brut du fichier", content[:10000], height=200)
    st.write(f"Longueur du contenu lu : {len(content)} caractères")
    st.text_area("Aperçu", content[-500:], height=200)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        st.error(f"Erreur JSON : {e}")
        st.stop()

    pages = data["pages"] 

# Construire le graphe
net = Network(height="600px", width="100%", directed=True)

# Récupérer les IDs
node_ids = {page["id"] for page in pages}

# Chercher les cibles de tous les choix
targets = {choice["nextPage"] for page in pages for choice in page.get("choices", [])}

# Le dernier noeud = un noeud qui n'apparaît jamais dans les targets
end_nodes = node_ids - targets

for page in pages:
    color = None
    if page["id"] == "p1":
        color = "green"
    elif page["id"] in end_nodes:
        color = "red"

    net.add_node(page["id"], label=page["id"], title=page["text"], color=color)
    
for page in pages:
    for choice in page.get("choices", []):
        target = choice["nextPage"]
        if target not in node_ids:
            # Crée un noeud fantôme (gris) pour les pages manquantes
            net.add_node(target, label=target, color="gray")
            node_ids.add(target)
        net.add_edge(page["id"], target, title=choice["text"], label=choice["text"])

# Générer HTML et afficher dans Streamlit
net.save_graph("graph.html")
with open("graph.html", "r", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=600, scrolling=True)