import streamlit as st
import sqlite3
import hashlib
import uuid
import os
from google import genai

# ===================================================================================================
#    [STREAMLIT PRODUCTION VERSION - TOTAL PROTECTION] - JAHORI WINDOW EMBA SAAS (PART 1)
# ===================================================================================================

# 1. Configuración de la pestaña del navegador
st.set_page_config(page_title="JAHORI - Discover Your Blind Spots", page_icon="🔮", layout="centered")

# 2. Inyección de Estilo CSS Corporativo (Fija de forma estricta el inicio azul y la rejilla interna)
st.markdown("""
    <style>
    /* Fondo blanco limpio estilo Google */
    .stApp { background-color: #FFFFFF; }
    
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .compliance-box { background-color: #F1F3F9; border-left: 4px solid #3E63DD; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    
    /* 💡 REGLA DE ALINEACIÓN DE LA HOME (Solo actúa si NO hay barra lateral) */
    .stApp:not(:has(div[data-testid="stSidebar"])) div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important; /* Fuerza a mantener la fila horizontal en móviles */
        justify-content: center !important;
        align-items: center !important;
        gap: 20px !important;
        width: 100% !important;
        max-width: 400px !important;
        margin: 25px auto 0 auto !important;
    }
    
    .stApp:not(:has(div[data-testid="stSidebar"])) div[data-testid="column"] {
        width: 50% !important;
        flex: 1 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stApp:not(:has(div[data-testid="stSidebar"])) div[data-testid="stElementContainer"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* 💡 REGLA DE COLOR DE LA HOME: Obliga a los botones de inicio a ser azules y redondeados */
    .stApp:not(:has(div[data-testid="stSidebar"])) .stButton>button { 
        width: 160px !important; 
        background-color: #3E63DD !important; 
        color: white !important; 
        border-radius: 20px !important; 
        border: 1px solid #3E63DD !important; 
        padding: 10px 20px !important; 
        font-weight: 500 !important;
        font-size: 14.5px !important; 
        cursor: pointer !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
        white-space: nowrap !important;
    }
    .stApp:not(:has(div[data-testid="stSidebar"])) .stButton>button:hover { 
        background-color: #2E4cbd !important; 
        border-color: #2E4cbd !important; 
    }
    
    /* 💡 MATRIZ INTERNA DE ADJETIVOS (2 COLUMNAS): Configuración fija e independiente */
    .stApp:has(div[data-testid="stSidebar"]) div[data-testid="stHorizontalBlock"] {
        max-width: 100% !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        gap: 15px !important;
    }
    .stApp:has(div[data-testid="stSidebar"]) div[data-testid="column"] {
        width: 50% !important;
        max-width: 50% !important;
        flex: 1 1 50% !important;
    }
    
    /* Estilizado de las tarjetas de adjetivos: amplias y alineadas horizontalmente */
    div[data-testid="stCheckbox"] {
        background-color: #F8F9FA !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        border: 1px solid #E4E7EB !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        height: 50px !important; /* Altura fija que clava la simetría horizontal */
        display: flex !important;
        align-items: center !important; 
        transition: all 0.2s ease-in-out !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stCheckbox"]:hover {
        background-color: #F1F3F9 !important;
        border-color: #3E63DD !important;
    }
    div[data-testid="stCheckbox"] label {
        display: flex !important;
        align-items: center !important;
        height: 100% !important;
        width: 100% !important;
    }
    div[data-testid="stCheckbox"] label p {
        color: #333333 !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        white-space: nowrap !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Inicialización síncrona de la Base de Datos SQLite
def init_db():
    conn = sqlite3.connect("reflex.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, share_token TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS self_assessment (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, adjectives TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, anonymous_adjectives TEXT)")
    conn.commit()
    return conn

conn = init_db()

JOHARI_ADJECTIVES = [
    "Able", "Accepting", "Adaptable", "Bold", "Brave", "Calm", "Caring", "Cheerful", "Clever", "Complex", 
    "Confident", "Dependable", "Dignified", "Empathetic", "Energetic", "Friendly", "Giving", "Happy", "Helpful", "Idealistic", 
    "Independent", "Ingenious", "Intelligent", "Introverted", "Kind", "Knowledgeable", "Logical", "Loving", "Mature", "Modest"
]
# ===================================================================================================
#    [STREAMLIT PRODUCTION VERSION] - PEER PANEL & AUTHENTICATION NATIVE (PART 2)
# ===================================================================================================

query_params = st.query_params

if "token" in query_params:
    target_token = str(query_params["token"])
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE share_token = ?", (target_token,))
    user_data = cursor.fetchone()
    
    if not user_data:
        st.error("❌ Invalid Link. This evaluation token does not exist or has expired.")
    else:
        target_user_id = int(user_data[0]) if isinstance(user_data, tuple) else int(user_data)
        st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 42px;'><span style='color: #3E63DD;'>Evaluate Your</span> Friend</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666666; font-size: 16px;'>Your anonymous feedback is 100% confidential and RODO compliant.</p>", unsafe_allow_html=True)
        st.markdown("<div class='compliance-box'><strong>🔒 RODO Compliance Shield:</strong> Anonymous form. No tracking.</div>", unsafe_allow_html=True)
        
        st.write("Select 3 to 10 adjectives that best describe your colleague:")
        
        selected_friend_words = []
        # Rejilla fija de 2 columnas para el panel público de amigos
        cols = st.columns(2)
        for i, adj in enumerate(JOHARI_ADJECTIVES):
            with cols[i % 2]:
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
    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.page = "Home"

    if st.session_state.user is None:
        if st.session_state.page == "Home":
            st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 48px; margin-top: 50px;'><span style='color: #3E63DD;'>Discover Your</span> Blind Spots</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #555555; font-size: 18px; max-width: 580px; margin: 0 auto 10px auto; line-height: 1.6;'>Analyze your personality with the Johari Window powered by Artificial Intelligence. 100% private. No software installations required.</p>", unsafe_allow_html=True)
            
            st.write("")
            col1, col2 = st.columns(2)
            with col1: btn_get = st.button("Get Started ➡️", key="home_azul_get")
            with col2: btn_log = st.button("Log In", key="home_azul_log")
                
            if btn_get: st.session_state.page = "Register"; st.rerun()
            if btn_log: st.session_state.page = "Login"; st.rerun()
                    
        elif st.session_state.page == "Register":
            st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 36px;'><span style='color: #3E63DD;'>Create Your</span> Account</h1>", unsafe_allow_html=True)
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
                        # Extracción segura de la posición 0 al registrarse
                        st.session_state.user = int(user_data[0]) if user_data else None
                        st.session_state.page = "Dashboard"; st.rerun()
                    except sqlite3.IntegrityError: st.error("This username is already taken.")
                        
        elif st.session_state.page == "Login":
            st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 36px;'>Log <span style='color: #3E63DD;'>In</span></h1>", unsafe_allow_html=True)
            log_user = st.text_input("Username")
            log_pass = st.text_input("Password", type="password")
            if st.button("Sign In"):
                hashed = hashlib.sha256(log_pass.encode()).hexdigest()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM user WHERE username = ? AND password_hash = ?", (log_user, hashed))
                result = cursor.fetchone()
                if result:
                    # 💡 SOLUCCIÓN DEFINITIVA: Extrae la posición cero result[0] para fulminar el TypeError al loguearse
                    st.session_state.user = int(result[0])
                    st.session_state.page = "Dashboard"; st.rerun()
                else: st.error("Incorrect username or password.")
                    
        if st.session_state.page != "Home":
            if st.button("⬅️ Back to Home"): st.session_state.page = "Home"; st.rerun()
# ===================================================================================================
#    [STREAMLIT PRODUCTION VERSION] - USER DASHBOARD & AI REPORT (PART 3)
# ===================================================================================================
    else:
        st.sidebar.markdown(f"### 🔒 Session Secure")
        if st.sidebar.button("🚪 Log Out"): st.session_state.user = None; st.session_state.page = "Home"; st.rerun()
            
        current_user_id = int(st.session_state.user)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id = ?", (current_user_id,))
        f_count_data = cursor.fetchone()
        f_count = int(f_count_data[0]) if f_count_data else 0
        
        st.markdown("<h1 style='font-size:28px; font-weight:700;'>Your Johari Control Panel</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🎯 Step 1: Self Assessment & Link", "📊 Step 2: Results & AI Report"])
        
        with tab1:
            st.write("Select 3 to 10 adjectives that best describe you today:")
            cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (current_user_id,))
            existing_assessment = cursor.fetchone()
            saved_words = existing_assessment[0].split(",") if existing_assessment else []
            
            selected_my_words = []
            # Rejilla fija de 2 columnas para tu autoevaluación privada
            cols = st.columns(2)
            for i, adj in enumerate(JOHARI_ADJECTIVES):
                with cols[i % 2]:
                    if st.checkbox(adj, key=f"my_{adj}", value=(adj in saved_words)): selected_my_words.append(adj)
                        
            if st.button("Save Assessment"):
                if len(selected_my_words) < 3 or len(selected_my_words) > 10: st.error("Please select between 3 and 10 adjectives.")
                else:
                    my_str = ",".join(selected_my_words)
                    cursor.execute("INSERT OR REPLACE INTO self_assessment (user_id, adjectives) VALUES (?, ?)", (current_user_id, my_str))
                    conn.commit()
                    st.success("Your self-assessment has been securely recorded!")
            
            st.markdown("### 🔗 Distribute Your Anonymous Link")
            cursor.execute("SELECT share_token FROM user WHERE id = ?", (current_user_id,))
            token_res = cursor.fetchone()
            user_token = token_res[0] if token_res else "error"
            try:
                ctx = st.context
                current_host = ctx.headers.get("Host", "localhost:8501")
                protocol = "https" if "streamlit.app" in current_host else "http"
                generated_url = f"{protocol}://{current_host}/?token={user_token}"
            except Exception: generated_url = f"http://localhost:8501/?token={user_token}"
            st.code(generated_url)
            st.markdown(f"Current progress: **{f_count}/3 evaluations received**.")
            
        with tab2:
            if f_count < 3: st.warning(f"Threshold not met. You need at least 3 evaluations. (Current: {f_count}/3)")
            else:
                cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (current_user_id,))
                user_res = cursor.fetchone()
                user_set = set(user_res[0].split(",")) if user_res else set()
                cursor.execute("SELECT anonymous_adjectives FROM feedback WHERE user_id = ?", (current_user_id,))
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
                
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"👐 **1. Open Area:** \n\n {', '.join(open_area) if open_area else 'None'}")
                    st.error(f"🔒 **3. Hidden Area:** \n\n {', '.join(hidden_area) if hidden_area else 'None'}")
                with c2:
                    st.warning(f"👁️ **2. Blind Area:** \n\n {', '.join(blind_area) if blind_area else 'None'}")
                    st.success(f"🔮 **4. Unknown Area:** \n\n Undiscovered qualities left to explore.")
                
                st.markdown("<br><h3 style='color: #3E63DD; font-weight: 700;'>🧠 Executive Coaching Report</h3>", unsafe_allow_html=True)
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key: st.error("API Secret Key missing.")
                else:
                    with st.spinner("Gemini is analyzing your psychological vectors..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            prompt_payload = f"Act as an expert leadership coach specialized in the Johari Window model. My assessment: {', '.join(user_set)}. Peer reputation attributes: {', '.join(all_friends_list)}. Please write an analysis of my blind spots and an actionable plan in exactly two short prose paragraphs in English."
                            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_payload)
                            st.write(response.text)
                        except Exception as e: st.error(f"Google GenAI Connection temporary suspended: {e}")
