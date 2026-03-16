import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. PERSONALIZZAZIONE ESTETICA (CSS) ---
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
    .stChatFloatingInputContainer { background-color: #1E2328 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTIONE API KEY (ANTIPANICO) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None

# --- 4. LOGICA DI ACCESSO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Accesso IusAlgor Pro")
    with st.container():
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Entra nel Sistema"):
            if user == "admin" and password == "ius2024": # Puoi cambiare queste credenziali
                st.session_state.logged_in = True
                st.session_state.user_name = user
                st.rerun()
            else:
                st.error("Credenziali non valide")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    st.header("Console di Controllo")
    
    if not api_key:
        api_key = st.text_input("🔑 Inserisci API Key per sessione locale", type="password")

    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documentazione Tecnica", type=['pdf', 'txt'])
    
    st.markdown("---")
    toggle_dettaglio = st.toggle("Analisi Approfondita", value=True)
    livello_dettaglio = "Completa" if toggle_dettaglio else "Riassuntiva"
    
    if st.button("Log-out"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.markdown(f"Benvenuto operatore: **{st.session_state.user_name}**")

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chiedi a IusAlgor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # --- LOGICA DI RISPOSTA DINAMICA (IL CUORE DELLA TUA RICHIESTA) ---
                if uploaded_file is not None:
                    # Istruzioni se c'è un documento: Modalità Auditor
                    sys_instr = (
                        "Agisci come IusAlgor Pro, esperto legale IA. Hai un documento tecnico. "
                        "Analizzalo con rigore formale, citando conformità e rischi. "
                    )
                    if livello_dettaglio == "Completa":
                        sys_instr += "Struttura la risposta in: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE."
                else:
                    # Istruzioni senza documento: Modalità Assistente Cordiale
                    sys_instr = (
                        "Sei IusAlgor Pro. Se l'utente ti saluta o fa domande generali, rispondi in modo "
                        "cordiale e professionale. Spiega che sei pronto ad analizzare i documenti che "
                        "caricherà nella sidebar. Non fare analisi tecniche se non hai file caricati."
                    )

                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    system_instruction=sys_instr
                )
                
                # Ricostruzione storico
                history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=history)

                with st.spinner('Elaborazione in corso...'):
                    if uploaded_file is not None:
                        # Gestione file
                        ext = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = tmp.name
                        
                        g_file = genai.upload_file(tmp_path)
                        response = chat.send_message([g_file, prompt])
                        os.remove(tmp_path)
                    else:
                        # Solo testo
                        response = chat.send_message(prompt)

                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")
else:
    st.info("👈 Configura la chiave API nei Secrets o nella barra laterale.")
