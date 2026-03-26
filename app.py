import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. CSS (Blu Notte e Oro) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #05070A !important; border-right: 2px solid #D4AF37; }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #D4AF37 !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0E1117 !important; font-weight: bold; width: 100%; border-radius: 5px; }
    .stChatInputContainer textarea { border: 1px solid #D4AF37 !important; background-color: #1B212C !important; color: white !important; }
    
    /* Logo nella chat */
    div[data-testid="stChatMessageAvatarAssistant"] {
        background-image: url("app/static/logo.png");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        background-color: #0E1117; border: 1px solid #D4AF37;
    }
    div[data-testid="stChatMessageAvatarAssistant"] svg { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTIONE NOME ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if not st.session_state.user_name:
    st.title("⚖️ Benvenuto in IusAlgor Pro")
    nome = st.text_input("Come si chiama l'avvocato oggi?", placeholder="Inserisci nome...")
    if st.button("Inizia Sessione"):
        if nome:
            st.session_state.user_name = nome
            st.rerun()
    st.stop()

# --- 4. API KEY ---
api_key = st.secrets.get("GEMINI_API_KEY")

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    st.header("Console di Controllo")
    st.write(f"👤 Utente: **{st.session_state.user_name}**")
    if not api_key:
        api_key = st.text_input("🔑 API Key", type="password")
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documenti", type=['pdf', 'txt'])
    st.markdown("---")
    if st.button("🎧 Parla con un operatore"):
        st.info("Connessione in corso con lo studio Giuseppe KTM...")

# --- 6. CHAT ---
st.title("⚖️ IusAlgor Pro")

if api_key:
    genai.configure(api_key=api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Chiedi un'analisi legale..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # FIX: Chiamata pulita al modello stabile v1
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Istruzioni passate come "contesto" invece che system_instruction
                sys_msg = f"Agisci come IusAlgor Pro per {st.session_state.user_name}. Schema: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI."
                
                if uploaded_file:
                    ext = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    g_file = genai.upload_file(tmp_path)
                    # Inviamo istruzioni + file + prompt tutto insieme
                    response = model.generate_content([sys_msg, g_file, prompt])
                    os.remove(tmp_path)
                else:
                    response = model.generate_content(f"{sys_msg}\n\nDomanda: {prompt}")

                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"Errore: {str(e)}")
else:
    st.info("👈 Inserisci l'API Key.")
