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

# --- 4. LOGICA DI ACCESSO DINAMICA ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Accesso Sistema IusAlgor")
    
    # Qui l'utente sceglie come farsi chiamare
    user_chosen_name = st.text_input("Inserisci il tuo Nome Operatore")
    password_input = st.text_input("Password di Sistema", type="password")
    
    if st.button("Attiva Sessione"):
        # Controlliamo solo la password, accettiamo qualsiasi nome non vuoto
        if password_input == "password" and user_chosen_name.strip() != "":
            st.session_state.logged_in = True
            st.session_state.user_name = user_chosen_name
            st.rerun()
        elif user_chosen_name.strip() == "":
            st.warning("Per favore, inserisci un nome operatore.")
        else:
            st.error("Password errata.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    # Mostra il nome scelto dall'utente
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("🔑 API Key locale", type="password")

    uploaded_file = st.file_uploader("📂 Carica Documento", type=['pdf', 'txt'])
    st.markdown("---")
    toggle_dettaglio = st.toggle("Analisi Approfondita", value=True)
    
    if st.button("Termina Sessione"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. CHAT INTERFACCIA ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Operatore in sessione: {st.session_state.user_name}")

# Gestione Avatar (File locale se esiste, altrimenti emoji)
AVATAR_AI = "gemini_logo.png" if os.path.exists("gemini_logo.png") else "✨"
AVATAR_USER = "👤"

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = AVATAR_AI if message["role"] == "assistant" else AVATAR_USER
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Chiedi a IusAlgor, {st.session_state.user_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_AI):
            try:
                # L'IA ora sa esattamente chi la sta interrogando
                if uploaded_file is not None:
                    sys_instr = (
                        f"Sei IusAlgor Pro. Ti stai interfacciando con l'operatore {st.session_state.user_name}. "
                        "Analizza il file caricato con rigore usando: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE."
                    )
                else:
                    sys_instr = (
                        f"Sei IusAlgor Pro. Saluta cordialmente {st.session_state.user_name} e offri il tuo aiuto. "
                        "Specifica che sei pronto ad analizzare i documenti caricati nella sidebar."
                    )

                model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)

                with st.spinner('Elaborazione in corso...'):
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
