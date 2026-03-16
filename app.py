import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. PERSONALIZZAZIONE ESTETICA (CSS) ---
# Palette: Blu Notte Logo (#14213D), Oro (#D4AF37), Antracite (#1E2328)
st.markdown(f"""
    <style>
    /* Sfondo generale e font */
    .stApp {{
        background-color: #1E2328;
        color: #FFFFFF;
    }}
    
    /* Sidebar più scura con richiamo blu */
    section[data-testid="stSidebar"] {{
        background-color: #0F172A !important;
        border-right: 1px solid #D4AF37;
    }}
    
    /* Titoli e testi in Oro */
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p {{
        color: #D4AF37 !important;
    }}
    
    /* Pulsante Operatore (Blu con bordi oro) */
    div.stButton > button:first-child {{
        background-color: #14213D !important;
        color: #D4AF37 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }}
    
    div.stButton > button:first-child:hover {{
        background-color: #D4AF37 !important;
        color: #14213D !important;
    }}

    /* Input e Chat Box */
    .stTextInput>div>div>input {{
        background-color: #2D3339 !important;
        color: white !important;
        border: 1px solid #14213D !important;
    }}
    
    /* Styling messaggi chat */
    [data-testid="stChatMessage"] {{
        background-color: #262D33;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTIONE NOME UTENTE ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if not st.session_state.user_name:
    st.title("⚖️ Benvenuto in IusAlgor Pro")
    nome_input = st.text_input("Prima di iniziare l'audit, come ti chiami?", placeholder="Inserisci il tuo nome...")
    if st.button("Inizia Sessione"):
        if nome_input:
            st.session_state.user_name = nome_input
            st.rerun()
        else:
            st.warning("Per favore, inserisci un nome per procedere.")
    st.stop()

# --- 4. RECUPERO API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    st.header("Console di Controllo")
    st.write(f"👤 Utente: **{st.session_state.user_name}**")
    
    if not api_key:
        api_key = st.text_input("🔑 Gemini API Key", type="password")

    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documentazione", type=['pdf', 'txt'])
    
    st.markdown("---")
    toggle_dettaglio = st.toggle("Analisi Approfondita", value=True)
    livello_dettaglio = "Completa" if toggle_dettaglio else "Riassuntiva"
    
    st.info(f"🔵 **Modalità:** {livello_dettaglio}\n\n🤖 **Motore:** Gemini 2.5 Flash")

    # --- TASTO BLU OPERATORE ---
    st.markdown("---")
    if st.button("📞 Collegati con un operatore"):
        st.toast("Connessione con l'assistenza legale in corso...")

# --- 6. INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.markdown(f"##### *Audit di Conformità Legale per Sistemi di IA - Benvenuto, {st.session_state.user_name}*")

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        # Usa il logo per l'assistente, l'icona utente per l'utente
        avatar = "logo.png" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chiedi un'analisi legale..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="logo.png"):
            try:
                sys_instr = f"Agisci come IusAlgor Pro, esperto legale IA. Ti stai rivolgendo a {st.session_state.user_name}. "
                if livello_dettaglio == "Completa":
                    sys_instr += "Analizza in dettaglio: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE."
                else:
                    sys_instr += "Fornisci un verdetto rapido e sintetico."

                model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                
                history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=history)

                with st.spinner(f'Analisi in corso per {st.session_state.user_name}...'):
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
                st.error(f"❌ Errore: {str(e)}")
else:
    st.info("👈 Inserisci la tua API Key nella barra laterale per sbloccare l'analisi.")