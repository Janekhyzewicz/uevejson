import os
import webbrowser
import threading

def run_streamlit():
    os.system('streamlit run lecteur_visual_json.py --server.headless true')

threading.Thread(target=run_streamlit).start()
webbrowser.open("http://localhost:8501")