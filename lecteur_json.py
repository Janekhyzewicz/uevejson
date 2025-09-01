import json
import streamlit as st
import io

st.set_page_config(page_title="Éditeur de scénario", layout="wide")

st.title("📖 Éditeur de scénario interactif")

# --- Charger le JSON ---
uploaded_file = st.file_uploader("Importer un fichier JSON", type="json")
if uploaded_file:
    # uploaded_file est un flux binaire -> il faut lire et décoder
    content = uploaded_file.getvalue().decode("utf-8-sig")
    st.text_area("Contenu brut du fichier", content[:500], height=200)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        st.error(f"Erreur JSON : {e}")
        st.stop()

    pages = data["pages"] 

    # Liste des pages
    page_ids = [page["id"] for page in pages]
    selected_page = st.sidebar.selectbox("Sélectionner une page", page_ids)

    # Trouver la page active
    page = next(p for p in pages if p["id"] == selected_page)

    # --- Formulaire d'édition ---
    st.subheader(f"Édition de la page {page['id']}")
    page["id"] = st.text_input("ID", value=page["id"])
    page["text"] = st.text_area("Texte", value=page["text"], height=150)
    page["backgroundImage"] = st.text_input("Image de fond", value=page.get("backgroundImage", ""))
    page["portraitImage"] = st.text_input("Portrait", value=page.get("portraitImage", ""))

    st.write("### Choix")
    for choice in page.get("choices", []):
        st.text_input("ID du choix", value=choice["id"], key=f"choice_id_{choice['id']}")
        st.text_input("Texte du choix", value=choice["text"], key=f"choice_text_{choice['id']}")
        st.text_input("Page suivante", value=choice["nextPage"], key=f"choice_next_{choice['id']}")

    # --- Bouton pour sauvegarder ---
    if st.button("Exporter JSON"):
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button("Télécharger le JSON", json_str, file_name="scenario.json", mime="application/json")