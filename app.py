import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# --- 2. GESTIONE STATO DI ACCESSO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. SCHERMATA DI LOGIN (NUOVO DESIGN MOBILE-FIRST) ---
if not st.session_state.logged_in:
    # INIEZIONE CSS SPECIFICO PER IL LOGIN
    st.markdown("""
    <style>
    /* Sfondo notturno (gradiente viola/scuro) per tutta la pagina */
    .stApp {
        background: linear-gradient(180deg, #1A0B2E 0%, #3B185F 100%) !important;
    }
    
    /* Nasconde la barra laterale e i menu superiori durante il login */
    [data-testid="collapsedControl"], section[data-testid="stSidebar"], header {
        display: none !important;
    }
    
    /* Crea la "Card Bianca" sulla colonna centrale */
    [data-testid="column"]:nth-of-type(2) {
        background-color: #FFFFFF !important;
        padding: 40px 30px !important;
        border-radius: 24px !important;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.4) !important;
        margin-top: -15px;
    }
    
    /* Stile Titolo (Nero scuro elegante) */
    .welcome-title {
        color: #111827 !important; 
        font-size: 32px !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    
    /* Stile Sottotitolo (Grigio medio) */
    .welcome-sub {
        color: #6B7280 !important; 
        text-align: center;
        font-size: 14px !important;
        margin-bottom: 25px;
    }
    
    /* Colore testo delle etichette (email, password) in grigio scuro */
    .stTextInput label p { color: #374151 !important; font-weight: 600; }
    
    /* Stile del bottone NEXT -> (Oro elegante per richiamare il tema interno) */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #E6B31E 0%, #D4AF37 100%) !important;
        color: #111827 !important; /* Testo scuro per massimo contrasto sull'oro */
        border: none !important;
        border-radius: 30px !important;
        padding: 12px !important;
        width: 100% !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        box-shadow: 0px 8px 15px rgba(212, 175, 55, 0.3) !important;
        transition: transform 0.2s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    # LAYOUT A COLONNE (Simula lo schermo stretto del mobile)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # HERO AREA: Immagine IusAlgor
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            # Placeholder se l'immagine non c'è
            st.markdown('<div style="height: 150px; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px; text-align: center; line-height: 150px; color: white;">[Area Immagine]</div>', unsafe_allow_html=True)

        # CONTENITORE FORM
        st.markdown('<p class="welcome-title">WELCOME!</p>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-sub">Accedi al sistema IusAlgor Pro</p>', unsafe_allow_html=True)

        user_chosen_name = st.text_input("👤 email or username")
        password_input = st.text_input("🔒 password", type="password")

        # RIGA: Remember me & Forgot Password
        c_left, c_right = st.columns(2)
        with c_left:
            st.checkbox("Remember me")
        with c_right:
            st.markdown('<p style="text-align: right; margin-top: 10px;"><a href="#" style="color: #111827; font-size: 14px; text-decoration: none; font-weight: bold;">Forgot password?</a></p>', unsafe_allow_html=True)

        st.write("") # Spazio

        # BOTTONE E LOGICA DI ACCESSO
        if st.button("NEXT →"):
            if password_input == "password" and user_chosen_name.strip() != "":
                st.session_state.logged_in = True
                st.session_state.user_name = user_chosen_name
                st.rerun() # Ricarica l'app per entrare nella dashboard
            elif user_chosen_name.strip() == "":
                st.warning("Per favore, inserisci email o username.")
            else:
                st.error("Password errata.")
                
    st.stop() # Ferma l'esecuzione qui finché non si è loggati

# =====================================================================
# DA QUI IN POI: L'UTENTE È LOGGATO (DASHBOARD PRINCIPALE)
# =====================================================================

# --- 4. STILE DELLA DASHBOARD PRINCIPALE ---
st.markdown("""
    <style>
    .stApp { background-color: #1E2328; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #D4AF37; }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #D4AF37 !important; }
    /* Stile base per i bottoni nella dashboard */
    div.stButton > button:first-child {
        background-color: #14213D !important;
        color: #D4AF37 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GESTIONE API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None

# --- 6. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image(Image.open('logo.png'), width=250)
    
    st.header(f"👤 {st.session_state.user_name}")
    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("🔑 API Key locale", type="password")

    uploaded_file = st.file_uploader("📂 Carica Documento", type=['pdf', 'txt'])
    
    st.markdown("---")
    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Termina Sessione"):
        st.session_state.logged_in = False
        st.session_state.messages = [] 
        st.rerun()

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
            label="📥 Scarica Cronologia (.txt)",
            data=report_text,
            file_name=f"Analisi_IusAlgor_{st.session_state.user_name}.txt",
            mime="text/plain"
        )

# --- 7. CHAT INTERFACCIA ---
st.title("⚖️ IusAlgor Pro")
st.caption(f"Operatore in sessione: {st.session_state.user_name}")

AVATAR_AI = "gemini_logo.png" if os.path.exists("gemini_logo.png") else "✨"
AVATAR_USER = "👤"

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizza messaggi passati
    for message in st.session_state.messages:
        avatar = AVATAR_AI if message["role"] == "assistant" else AVATAR_USER
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Input utente e generazione risposta
    if prompt := st.chat_input(f"Chiedi a IusAlgor, {st.session_state.user_name}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_AI):
            try:
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
                
                with st.status("Elaborazione pratica in corso...", expanded=True) as status:
                    content_to_send = [prompt]
                    tmp_path = None
                    
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
                
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
            except Exception as e:
                st.error(f"Si è verificato un errore: {str(e)}")
else:
    st.info("👈 Configura l'API Key nella sidebar per iniziare.")
