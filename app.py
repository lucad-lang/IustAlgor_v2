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

# --- 3. SCHERMATA DI LOGIN (DESIGN NOTTURNO/ORO) ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #020617 100%) !important;
    }
    [data-testid="collapsedControl"], section[data-testid="stSidebar"], header {
        display: none !important;
    }
    .login-container {
        background-color: #FFFFFF !important;
        padding: 40px 30px;
        border-radius: 24px;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.6);
        max-width: 450px;
        margin: auto;
    }
    .welcome-title {
        color: #111827 !important; 
        font-size: 32px !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 5px;
    }
    .welcome-sub {
        color: #6B7280 !important; 
        text-align: center;
        margin-bottom: 25px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #E6B31E 0%, #D4AF37 100%) !important;
        color: #111827 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        width: 100% !important;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") # Spacer
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<p class="welcome-title">WELCOME!</p>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-sub">Accedi al sistema IusAlgor Pro</p>', unsafe_allow_html=True)

        user_input = st.text_input("👤 Email o Username", key="user_login")
        pass_input = st.text_input("🔒 Password", type="password", key="pass_login")

        if st.button("NEXT →"):
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
    </style>
    """, unsafe_allow_html=True)

# Recupero API Key
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("🔑 API Key locale", type="password")

    uploaded_files = st.file_uploader("📂 Carica Documenti", type=['pdf', 'txt'], accept_multiple_files=True)
    
    if uploaded_files:
        with st.expander("Anteprima Documenti"):
            for f in uploaded_files:
                st.markdown(f"**📄 {f.name}**")
                if f.name.endswith('.txt'):
                    st.caption("Contenuto TXT caricato.")
                elif f.name.endswith('.pdf'):
                    st.caption("Anteprima PDF disponibile nel report.")

    st.markdown("---")
    
    # --- TASTO: PARLA CON UN OPERATORE ---
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

    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.markdown("---")
        report_text = f"REPORT IUSALGOR PRO - Operatore: {st.session_state.user_name}\n" + "="*40 + "\n"
        for msg in st.session_state.messages:
            ruolo = "OPERATORE" if msg["role"] == "user" else "IUSALGOR"
            report_text += f"[{ruolo}]: {msg['content']}\n\n"
        
        st.download_button("📥 Scarica Report", data=report_text, file_name="Analisi_IusAlgor.txt")

# --- INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Operatore: {st.session_state.user_name} | Motore: Gemini 2.0 Flash")

if api_key:
    genai.configure(api_key=api_key)
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
                # Istruzioni di Sistema
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
                
                # Cleanup
                for path in temp_files:
                    if os.path.exists(path): os.remove(path)
                    
            except Exception as e:
                st.error(f"Errore: {str(e)}")
else:
    st.info("👈 Configura l'API Key nella sidebar.")
