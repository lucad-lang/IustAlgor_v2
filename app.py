import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. PERSONALIZZAZIONE ESTETICA ---
st.markdown("""
    <style>
    .stApp { background-color: #1E2328; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #D4AF37; }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #D4AF37 !important; }
    div.stButton > button:first-child {
        background-color: #14213D !important;
        color: #D4AF37 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTIONE API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None

# --- 4. LOGICA DI ACCESSO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Accesso Sistema IusAlgor")
    user_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    
    if st.button("Attiva Sessione"):
        if user_input == "username" and password_input == "password":
            st.session_state.logged_in = True
            st.session_state.user_name = user_input
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("🔑 API Key locale", type="password")

    uploaded_file = st.file_uploader("📂 Carica Documento", type=['pdf', 'txt'])
    st.markdown("---")
    toggle_dettaglio = st.toggle("Analisi Approfondita", value=True)
    livello_dettaglio = "Completa" if toggle_dettaglio else "Riassuntiva"
    
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. CHAT INTERFACCIA (CON LINK PNG GEMINI) ---
st.title("⚖️ IusAlgor Pro")

# Link PNG stabile per il logo di Gemini
AVATAR_AI = "https://i.imgur.com/7k799pP.png" 
AVATAR_USER = "👤"

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = AVATAR_AI if message["role"] == "assistant" else AVATAR_USER
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chiedi a IusAlgor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_AI):
            try:
                # Istruzioni intelligenti (niente icone fisse se non c'è il file)
                if uploaded_file is not None:
                    sys_instr = f"Sei IusAlgor Pro. L'operatore {st.session_state.user_name} ha caricato un file. Analizzalo con rigore legale usando obbligatoriamente i titoli: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE."
                else:
                    sys_instr = f"Sei IusAlgor Pro. Rispondi cordialmente a {st.session_state.user_name}. Non usare icone o sezioni tecniche di audit se non è stato caricato alcun file. Invita l'utente a caricare un documento per iniziare."

                model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)

                with st.spinner('Gemini sta elaborando...'):
                    if uploaded_file is not None:
                        ext = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = tmp.name
                        g_file = genai.upload_file(tmp_path)
                        response = chat.send_message([g_file, prompt])
                        os.remove(tmp_path)
                    else:
                        response = chat.send_message(prompt)

                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore: {str(e)}")
else:
    st.info("👈 Configura l'API Key.")
