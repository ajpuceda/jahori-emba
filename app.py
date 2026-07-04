import streamlit as st
import sqlite3
import hashlib
import uuid
from google import genai
import os

# ===================================================================================================
#    [STREAMLIT PRODUCTION VERSION] - JAHORI WINDOW EMBA SAAS (PART 1)
# ===================================================================================================

# 1. Configuración de la pestaña del navegador
st.set_page_config(page_title="JAHORI - Discover Your Blind Spots", page_icon="🔮", layout="centered")

# 2. Inyección de Estilo CSS Corporativo (Garantiza el diseño Minimalista Estilo Google en Móviles y PC)
st.markdown("""
    <style>
    /* Resetear fondos y forzar limpieza visual */
    .stApp { background-color: #FFFFFF; }
    
    /* Contenedor central estilo Google */
    .google-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding-top: 80px;
        padding-bottom: 20px;
        width: 100%;
    }
    
    /* 💡 FIX DE SIMETRÍA: Fuerza a las columnas de los botones a unirse en el centro exacto sin márgenes fantasma */
    .google-buttons {
        display: flex;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        width: 100% !important;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    
    /* Elimina el espacio vacío que Streamlit mete a la izquierda de la columna 1 */
    div.google-buttons [data-testid="column"] {
        width: auto !important;
        flex: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Tipografía ejecutiva limpia */
    .johari-title { font-weight: 700; color: #111111; font-size: 48px; margin-bottom: 12px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .johari-blue { color: #3E63DD; }
    .johari-subtitle { color: #555555; font-size: 18px; margin-bottom: 40px; max-width: 580px; line-height: 1.6; margin-left: auto; margin-right: auto; }
    
    /* Ajuste de botones premium redondeados idénticos */
    .stButton>button { 
        width: 140px !important; 
        background-color: #3E63DD !important; 
        color: white !important; 
        border-radius: 20px !important; 
        border: 1px solid #3E63DD !important; 
        padding: 8px 16px !important; 
        font-weight: 500 !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
        display: block !important;
    }

    
    /* Tipografía ejecutiva limpia */
    .johari-title { font-weight: 700; color: #111111; font-size: 48px; margin-bottom: 12px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .johari-blue { color: #3E63DD; }
    .johari-subtitle { color: #555555; font-size: 18px; margin-bottom: 40px; max-width: 580px; line-height: 1.6; margin-left: auto; margin-right: auto; }
    
    /* Ajuste de botones premium redondeados */
    .stButton>button { 
        width: 140px !important; 
        background-color: #3E63DD !important; 
        color: white !important; 
        border-radius: 20px !important; /* Bordes redondeados estilo Google */
        border: 1px solid #3E63DD !important; 
        padding: 8px 16px !important; 
        font-weight: 500 !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
        display: inline-block !important;
    }
    .stButton>button:hover { background-color: #2E4cbd !important; color: white !important; border-color: #2E4cbd !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }
    
    /* Variación estética para el segundo botón (Login estilo gris claro de Google) */
    div.google-buttons > div:nth-child(2) .stButton>button {
        background-color: #F8F9FA !important;
        color: #3C4043 !important;
        border: 1px solid #F8F9FA !important;
    }
    div.google-buttons > div:nth-child(2) .stButton>button:hover {
        background-color: #F1F3F4 !important;
        border-color: #DADCE0 !important;
        color: #202124 !important;
    }
    
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .compliance-box { background-color: #F1F3F9; border-left: 4px solid #3E63DD; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicialización síncrona de la Base de Datos SQLite en el disco duro
def init_db():
    conn = sqlite3.connect("reflex.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, share_token TEXT UNIQUE
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS self_assessment (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, adjectives TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, anonymous_adjectives TEXT)")
    conn.commit()
    return conn

conn = init_db()

# Los 30 adjetivos oficiales de la Ventana de Johari
JOHARI_ADJECTIVES = [
    "Able", "Accepting", "Adaptable", "Bold", "Brave", "Calm", "Caring", "Cheerful", "Clever", "Complex", 
    "Confident", "Dependable", "Dignified", "Empathetic", "Energetic", "Friendly", "Giving", "Happy", "Helpful", "Idealistic", 
    "Independent", "Ingenious", "Intelligent", "Introverted", "Kind", "Knowledgeable", "Logical", "Loving", "Mature", "Modest"
]
# ===================================================================================================
#    [STREAMLIT PRODUCTION BLINDADO V3 - REAL RENDER] - PEER PUBLIC PANEL & AUTHENTICATION (PART 2)
# ===================================================================================================

query_params = st.query_params

# 💡 VALIDADOR DE ENLACES: Busca el token criptográfico UUID en la URL para evitar hackeos
if "token" in query_params:
    target_token = str(query_params["token"])
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE share_token = ?", (target_token,))
    user_data = cursor.fetchone()
    
    if not user_data:
        st.error("❌ Invalid Link. This evaluation token does not exist or has expired.")
    else:
        target_user_id = int(user_data[0])
        st.markdown("<h1 class='johari-title'>Evaluate Your <span class='johari-blue'>Friend</span></h1>", unsafe_allow_html=True)
        st.markdown("<p class='johari-subtitle'>Your anonymous feedback is 100% confidential and RODO compliant.</p>", unsafe_allow_html=True)
        st.markdown("<div class='compliance-box'><strong>🔒 RODO Compliance Shield:</strong> Anonymous form. No names tracked.</div>", unsafe_allow_html=True)
        
        selected_friend_words = []
        cols = st.columns(4)
        for i, adj in enumerate(JOHARI_ADJECTIVES):
            with cols[i % 4]:
                if st.checkbox(adj, key=f"friend_{adj}"): selected_friend_words.append(adj)
                    
        if st.button("Submit Anonymous Feedback"):
            if len(selected_friend_words) < 3 or len(selected_friend_words) > 10:
                st.error("Please select between 3 and 10 adjectives.")
            else:
                feedback_str = ",".join(selected_friend_words)
                cursor.execute("INSERT INTO feedback (user_id, anonymous_adjectives) VALUES (?, ?)", (target_user_id, feedback_str))
                conn.commit()
                st.success("Thank you! Your feedback has been securely submitted.")
                st.balloons()
else:
    # 🔐 SISTEMA DE SESIONES Y NAVEGACIÓN PRIVADA DEL USUARIO
    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.page = "Home"

    if st.session_state.user is None:
        if st.session_state.page == "Home":
            # 💡 SOLUCCIÓN MAESTRA: Se encapsula TODO el HTML con su debida instrucción unsafe_allow_html=True
            st.markdown("""
                <div class='google-container'>
                    <h1 class='johari-title'><span class='johari-blue'>Discover Your</span> Blind Spots</h1>
                    <p class='johari-subtitle'>Analyze your personality with the Johari Window powered by Artificial Intelligence. 100% private. No software installations required.</p>
                    
                    <div class='google-buttons'>
                        <a href='?action=register' target='_self' style='text-decoration: none;'>
                            <button style='width: 140px; background-color: #3E63DD; color: white; border-radius: 20px; border: 1px solid #3E63DD; padding: 10px 16px; font-weight: 500; font-size: 14px; cursor: pointer;'>
                                Get Started
                            </button>
                        </a>
                        <a href='?action=login' target='_self' style='text-decoration: none;'>
                            <button style='width: 140px; background-color: #F8F9FA; color: #3C4043; border-radius: 20px; border: 1px solid #DADCE0; padding: 10px 16px; font-weight: 500; font-size: 14px; cursor: pointer;'>
                                Log In
                            </button>
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Captura interactiva de clics desde los botones HTML
            if "action" in query_params:
                selected_action = query_params["action"]
                st.query_params.clear()
                if selected_action == "register":
                    st.session_state.page = "Register"
                    st.rerun()
                elif selected_action == "login":
                    st.session_state.page = "Login"
                    st.rerun()
                    
        elif st.session_state.page == "Register":
            st.markdown("<h1 class='johari-title'><span class='johari-blue'>Create Your</span> Account</h1>", unsafe_allow_html=True)
            st.write("Choose a unique nickname. No email or personal data required.")
            
            new_user = st.text_input("Choose a Username")
            new_pass = st.text_input("Password", type="password")
            rodo = st.checkbox("I accept the anonymous data handling under RODO/RGPD guidelines.")
            
            if st.button("Sign Up"):
                if not rodo: st.error("You must accept the RODO terms to register.")
                elif not new_user or not new_pass: st.error("Please fill in all fields.")
                else:
                    hashed = hashlib.sha256(new_pass.encode()).hexdigest()
                    generated_token = str(uuid.uuid4())
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO user (username, password_hash, share_token) VALUES (?, ?, ?)", (new_user, hashed, generated_token))
                        conn.commit()
                        cursor.execute("SELECT id FROM user WHERE username = ?", (new_user,))
                        user_data = cursor.fetchone()
                        st.session_state.user = int(user_data[0]) if user_data else None
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    except sqlite3.IntegrityError: st.error("This username is already taken.")
                        
        elif st.session_state.page == "Login":
            st.markdown("<h1 class='johari-title'>Log <span class='johari-blue'>In</span></h1>", unsafe_allow_html=True)
            log_user = st.text_input("Username")
            log_pass = st.text_input("Password", type="password")
            
            if st.button("Sign In"):
                hashed = hashlib.sha256(log_pass.encode()).hexdigest()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM user WHERE username = ? AND password_hash = ?", (log_user, hashed))
                result = cursor.fetchone()
                if result:
                    st.session_state.user = int(result[0])
                    st.session_state.page = "Dashboard"
                    st.rerun()
                else: st.error("Incorrect username or password.")
                    
        if st.session_state.page != "Home":
            if st.button("⬅️ Back to Home"): 
                st.session_state.page = "Home"
                st.rerun()
# ===================================================================================================
#    [STREAMLIT PRODUCTION VERSION] - USER DASHBOARD, JOHARI MATRIX & GEMINI AI REPORT (PART 3)
# ===================================================================================================
    else:
        st.sidebar.markdown(f"### 🔒 Session Secure")
        if st.sidebar.button("🚪 Log Out"):
            st.session_state.user = None
            st.session_state.page = "Home"
            st.rerun()
            
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id = ?", (st.session_state.user,))
        f_count_data = cursor.fetchone()
        f_count = int(f_count_data[0]) if f_count_data else 0
        
        st.markdown("<h1 style='font-size:28px; font-weight:700;'>Your Johari Control Panel</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🎯 Step 1: Self Assessment & Link", "📊 Step 2: Results & AI Report"])
        
        with tab1:
            st.write("Select 3 to 10 adjectives that best describe you today:")
            cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (st.session_state.user,))
            existing_assessment = cursor.fetchone()
            saved_words = existing_assessment[0].split(",") if existing_assessment else []
            
            selected_my_words = []
            cols = st.columns(4)
            for i, adj in enumerate(JOHARI_ADJECTIVES):
                with cols[i % 4]:
                    if st.checkbox(adj, key=f"my_{adj}", value=(adj in saved_words)): selected_my_words.append(adj)
                        
            if st.button("Save Assessment"):
                if len(selected_my_words) < 3 or len(selected_my_words) > 10: st.error("Please select between 3 and 10 adjectives.")
                else:
                    my_str = ",".join(selected_my_words)
                    cursor.execute("INSERT OR REPLACE INTO self_assessment (user_id, adjectives) VALUES (?, ?)", (st.session_state.user, my_str))
                    conn.commit()
                    st.success("Saved successfully!")
            
            st.markdown("### 🔗 Distribute Your Anonymous Link")
            st.write("Copy this link and send it via WhatsApp or Slack to your colleagues:")
            
            cursor.execute("SELECT share_token FROM user WHERE id = ?", (st.session_state.user,))
            token_res = cursor.fetchone()
            user_token = token_res[0] if token_res else "error"
            
            try:
                ctx = st.context
                current_host = ctx.headers.get("Host", "localhost:8501")
                protocol = "https" if "streamlit.app" in current_host else "http"
                generated_url = f"{protocol}://{current_host}/?token={user_token}"
            except Exception:
                generated_url = f"http://localhost:8501/?token={user_token}"
            
            st.code(generated_url)
            st.markdown(f"Current progress: **{f_count}/3 evaluations received**.")
            
        with tab2:
            if f_count < 3:
                st.warning(f"Threshold not met. You need at least 3 evaluations. (Current: {f_count}/3)")
            else:
                cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (st.session_state.user,))
                user_res = cursor.fetchone()
                user_set = set(user_res[0].split(",")) if user_res else set()
                
                cursor.execute("SELECT anonymous_adjectives FROM feedback WHERE user_id = ?", (st.session_state.user,))
                feedbacks = cursor.fetchall()
                friends_set = set()
                all_friends_list = []
                for f in feedbacks:
                    if f and f[0]:
                        words = f[0].split(",")
                        friends_set.update(words)
                        all_friends_list.extend(words)
                
                open_area = user_set.intersection(friends_set)
                blind_area = friends_set.difference(user_set)
                hidden_area = user_set.difference(friends_set)
                
                # Pintar la cuadrícula limpia sin saltos de línea conflictivos
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"👐 **1. Open Area:** \n\n {', '.join(open_area) if open_area else 'None'}")
                    st.markdown("### 🔒 3. Hidden Area")
                    st.write(f"{', '.join(hidden_area) if hidden_area else 'None'}")
                with c2:
                    st.warning(f"👁️ **2. Blind Area:** \n\n {', '.join(blind_area) if blind_area else 'None'}")
                    st.markdown("### 🔮 4. Unknown Area")
                    st.write("Undiscovered qualities left to explore.")
                
                st.markdown("<br>### 🧠 Executive Coaching Report", unsafe_allow_html=True)
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key: st.error("API Secret Key missing.")
                else:
                    with st.spinner("Gemini is analyzing your psychological vectors..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            prompt_payload = f"Act as an expert leadership coach. My assessment: {', '.join(user_set)}. Peer feedback: {', '.join(all_friends_list)}. Analyze blind spots and give a personal plan in exactly two short paragraphs."
                            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_payload)
                            st.write(response.text)
                        except Exception as e: st.error(f"AI Interrupted: {e}")
