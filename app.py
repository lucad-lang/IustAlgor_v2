import streamlit as st
import google.generativeai as genai
import os
import tempfile
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
        background: #0f172a !important; /* Sfondo Blu Notte */
    }
    [data-testid="collapsedControl"], section[data-testid="stSidebar"], header {
        display: none !important;
    }
    
    /* Contenitore principale senza box bianco */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 50px;
    }

    /* Scritta WELCOME in Oro Metallizzato */
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

    /* Stile Input */
    div.stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    /* Pulsante NEXT Giallo/Oro */
    div.stButton > button:first-child {
        background-color: #facc15 !important;
        color: #000 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        padding: 10px 40px !important;
        border: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #eab308 !important;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        
        # Logo più piccolo
        if os.path.exists("logo.png"):
            st.image("logo.png", width=220)
        
        st.markdown('<p class="welcome-title">WELCOME!</p>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-sub">Accedi al sistema IusAlgor Pro</p>', unsafe_allow_html=True)

        user_input = st.text_input("👤 Email o Username", key="user_login")
        pass_input = st.text_input("🔒 Password", type="password", key="pass_login")

        if st.button("NEXT →"):
            # Credenziali di esempio: username qualsiasi e password "password"
            if pass_input == "password" and user_input.strip() != "":
                st.session_state.logged_in = True
                st.session_state.user_name = user_input
                st.rerun()
            else:
                st.error("Credenziali non valide.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# DASHBOARD PRINCIPALE (UTENTE LOGGATO)
# =====================================================================

# Configurazione API Key fissa
api_key = "AIzaSyAOKQnWIEnJebOPzoOr_SA2mCuiv-mHymY"
genai.configure(api_key=api_key)

st.markdown("""
    <style>
    .stApp { background-color: #1E2328; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #D4AF37; }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #D4AF37 !important; }
    
    .stSidebar div.stButton > button {
        background-color: #14213D !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        font-weight: bold;
        width: 100%;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image('logo.png', width=200)
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    uploaded_files = st.file_uploader("📂 Carica Documenti", type=['pdf', 'txt'], accept_multiple_files=True)
    
    if uploaded_files:
        with st.expander("Anteprima Documenti"):
            for f in uploaded_files:
                st.markdown(f"**📄 {f.name}**")

    st.markdown("---")
    
    if st.button("🎧 Parla con un operatore"):
        st.toast("Connessione ai server legali...", icon="⏳")
        st.info("⚠️ Posizione in coda: 1. Un professionista dello studio Giuseppe KTM sarà presto con lei.")

    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Termina Sessione"):
        st.session_state.logged_in = False
        st.session_state.messages = [] 
        st.rerun()

# --- INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Operatore: {st.session_state.user_name} | Motore: Gemini 2.0 Flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizzazione messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=("✨" if message["role"] == "assistant" else "👤")):
        st.markdown(message["content"])

# Input Utente
if prompt := st.chat_input("Chiedi un'analisi legale..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        try:
            sys_instr = (
                f"Sei IusAlgor Pro, assistente legale di {st.session_state.user_name}. "
                "Analizza i documenti forniti e rispondi rigorosamente in Markdown con questo schema:\n"
                "### AMBITI\n(Punti elenco)\n"
                "### ⚠️ RISCHI\n🔸 **[Titolo]**\n- Gravità: [X]\n- Riferimento: [Y]\n"
                "### 💡 AZIONI CORRETTIVE\n(Elenco numerato)"
            )

            model = genai.GenerativeModel(model_name='gemini-2.0-flash', system_instruction=sys_instr)
            
            with st.status("Analisi legale in corso...", expanded=True) as status:
                inputs = [prompt]
                temp_files = []
                
                if uploaded_files:
                    for f in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
                            tmp.write(f.getvalue())
                            temp_files.append(tmp.name)
                        g_file = genai.upload_file(temp_files[-1])
                        while g_file.state.name == "PROCESSING":
                            time.sleep(2)
                            g_file = genai.get_file(g_file.name)
                        inputs.append(g_file)
                
                response = model.generate_content(inputs)
                status.update(label="Audit completato!", state="complete")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Cleanup file temporanei
            for path in temp_files:
                if os.path.exists(path): os.remove(path)
                
        except Exception as e:
            st.error(f"Errore: {str(e)}")
