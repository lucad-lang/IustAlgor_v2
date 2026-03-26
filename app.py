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
    
    user_chosen_name = st.text_input("Inserisci il tuo Nome Operatore")
    password_input = st.text_input("Password di Sistema", type="password")
    
    if st.button("Attiva Sessione"):
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
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("🔑 API Key locale", type="password")

    uploaded_file = st.file_uploader("📂 Carica Documento", type=['pdf', 'txt'])
    
    st.markdown("---")
    # Bottone Nuova Analisi (Svuota Chat)
    if st.button("🗑️ Nuova Analisi (Svuota Chat)"):
        st.session_state.messages = []
        st.rerun()

    # Bottone Termina Sessione
    if st.button("🚪 Termina Sessione"):
        st.session_state.logged_in = False
        st.session_state.messages = [] # Puliamo anche la chat quando si esce
        st.rerun()

    # Funzione di Esportazione
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.markdown("---")
        st.subheader("📄 Esporta Risultati")
        
        report_text = f"REPORT SESSIONE IUSALGOR PRO\n"
        report_text += f"Operatore: {st.session_state.user_name}\n"
        report_text += "="*30 + "\n\n"
        
        for msg in st.session_state.messages:
            ruolo = "OPERATORE" if msg["role"] == "user" else "IUSALGOR"
            report_text += f"[{ruolo}]:\n{msg['content']}\n"
            report_text += "-"*20 + "\n"

        st.download_button(
            label="📥 Scarica Cronologia Chat (.txt)",
            data=report_text,
            file_name=f"Analisi_IusAlgor_{st.session_state.user_name}.txt",
            mime="text/plain"
        )

# --- 6. CHAT INTERFACCIA ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Operatore in sessione: {st.session_state.user_name}")

AVATAR_AI = "gemini_logo.png" if os.path.exists("gemini_logo.png") else "✨"
AVATAR_USER = "👤"

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra messaggi precedenti
    for message in st.session_state.messages:
        avatar = AVATAR_AI if message["role"] == "assistant" else AVATAR_USER
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Input utente
    if prompt := st.chat_input(f"Chiedi a IusAlgor, {st.session_state.user_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_AI):
            try:
                # Istruzioni di sistema avanzate
                sys_instr = (
                    f"Sei IusAlgor Pro, un assistente legale esperto. Ti interfacci con l'operatore {st.session_state.user_name}. "
                    "Quando analizzi un documento, restituisci l'output rigorosamente in formato Markdown. "
                    "Usa il grassetto per i termini chiave o le leggi citate. "
                    "Struttura SEMPRE la tua risposta in queste tre sezioni esatte:\n\n"
                    "### 🎯 AMBITI\n"
                    "(Fornisci un elenco puntato degli ambiti legali/amministrativi coinvolti)\n\n"
                    "### ⚠️ RISCHI\n"
                    "(Crea una tabella Markdown con tre colonne: 'Rischio Rilevato', 'Gravità (Alta/Media/Bassa)', e 'Riferimento nel testo')\n\n"
                    "### 💡 AZIONI CORRETTIVE\n"
                    "(Fornisci un elenco numerato dei passaggi pratici per mitigare i rischi rilevati)."
                )

                model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=sys_instr)
                
                # Indicatore di stato
                with st.status("Elaborazione pratica in corso...", expanded=True) as status:
                    content_to_send = [prompt]
                    tmp_path = None # Inizializziamo la variabile per sicurezza
                    
                    if uploaded_file is not None:
                        st.write("📥 Preparazione del documento allegato...")
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        st.write("☁️ Caricamento sul server sicuro IusAlgor...")
                        g_file = genai.upload_file(tmp_path)
                        content_to_send.append(g_file)
                    
                    st.write("🧠 Analisi legale e stesura del responso...")
                    response = model.generate_content(content_to_send)
                    
                    status.update(label="Analisi completata con successo!", state="complete", expanded=False)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # Pulizia sicura del file temporaneo
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
            except Exception as e:
                st.error(f"Si è verificato un errore: {str(e)}")
else:
    st.info("👈 Configura l'API Key nella sidebar per iniziare.")
