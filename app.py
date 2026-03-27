import streamlit as st
import google.generativeai as genai
import os
import tempfile
import base64
import time
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. GESTIONE STATO DI ACCESSO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. SCHERMATA DI LOGIN (DESIGN AGGIORNATO) ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp {
        background: #0f172a !important; 
    }
    [data-testid="collapsedControl"], section[data-testid="stSidebar"], header {
        display: none !important;
    }
    
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 50px;
    }

    .welcome-title {
        background: linear-gradient(to bottom, #cfac48 0%, #ffefbb 50%, #cfac48 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 5px;
        filter: drop-shadow(0px 2px 2px rgba(0,0,0,0.5));
    }

    .welcome-sub {
        color: #94a3b8 !important; 
        text-align: center;
        margin-bottom: 30px;
        font-size: 18px;
    }

    div.stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    div.stButton > button:first-child {
        background-color: #facc15 !important;
        color: #000 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        padding: 12px 40px !important;
        border: none !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=220)
        
        st.markdown('<p class="welcome-title">WELCOME!</p>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-sub">Accedi al sistema IusAlgor Pro</p>', unsafe_allow_html=True)

        user_chosen_name = st.text_input("👤 Email o Username")
        password_input = st.text_input("🔒 Password", type="password")

        if st.button("NEXT →"):
            if password_input == "password" and user_chosen_name.strip() != "":
                st.session_state.logged_in = True
                st.session_state.user_name = user_chosen_name
                st.rerun()
            else:
                st.error("Credenziali non valide.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# DASHBOARD PRINCIPALE
# =====================================================================

# API Key Fissa
api_key = "AIzaSyAOKQnWIEnJebOPzoOr_SA2mCuiv-mHymY"
genai.configure(api_key=api_key)

st.markdown("""
    <style>
    .stApp { background-color: #1E2328; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #D4AF37; }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #D4AF37 !important; }
    
    /* Bottoni Sidebar */
    .stSidebar div.stButton > button {
        background-color: #14213D !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        font-weight: bold;
        width: 100%;
        margin-bottom: 10px;
    }
    /* Bottone Operatore (Speciale) */
    .btn-operator > div > button {
        background: linear-gradient(90deg, #D4AF37 0%, #FACC15 100%) !important;
        color: #000 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image('logo.png', width=200)
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    # --- NUOVO PULSANTE OPERATORE ---
    st.markdown('<div class="btn-operator">', unsafe_allow_html=True)
    if st.button("🎧 Collega con un operatore"):
        with st.spinner("Ricerca operatore disponibile..."):
            time.sleep(2)
            st.toast("Connessione stabilita con l'ufficio legale.", icon="✅")
            st.info("⚠️ **Avviso:** Tutti i nostri legali sono attualmente occupati. Verrai ricontattato entro 5 minuti all'indirizzo associato al profilo.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    uploaded_files = st.file_uploader("📂 Carica Documenti", type=['pdf', 'txt'], accept_multiple_files=True)
    
    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Termina Sessione"):
        st.session_state.logged_in = False
        st.session_state.messages = [] 
        st.rerun()

# --- INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Modalità: Analisi Documentale AI | Operatore: {st.session_state.user_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=("✨" if message["role"] == "assistant" else "👤")):
        st.markdown(message["content"])

if prompt := st.chat_input("Inserisci quesito legale..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        try:
            sys_instr = (
                f"Sei IusAlgor Pro, assistente legale di {st.session_state.user_name}. "
                "Analizza i documenti e rispondi rigorosamente in Markdown con AMBITI, RISCHI e AZIONI CORRETTIVE."
            )
            model = genai.GenerativeModel(model_name='gemini-2.0-flash', system_instruction=sys_instr)
            
            with st.status("Analisi in corso...", expanded=True) as status:
                inputs = [prompt]
                temp_files = []
                if uploaded_files:
                    for f in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
                            tmp.write(f.getvalue())
                            temp_files.append(tmp.name)
                        g_file = genai.upload_file(temp_files[-1])
                        while g_file.state.name == "PROCESSING":
                            time.sleep(1)
                            g_file = genai.get_file(g_file.name)
                        inputs.append(g_file)
                
                response = model.generate_content(inputs)
                status.update(label="Audit completato!", state="complete")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            for path in temp_files:
                if os.path.exists(path): os.remove(path)
                
        except Exception as e:
            st.error(f"Errore tecnico: {str(e)}")
