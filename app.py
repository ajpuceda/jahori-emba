import streamlit as st
import sqlite3
import hashlib
import uuid
import os
from google import genai

# ===================================================================================================
#    [JAHORI WINDOW EMBA SAAS - PRODUCTION BLINDADO V11] - CONFIGURACIÓN Y ESTILOS (PART 1)
# ===================================================================================================

# 1. Configuración de la pestaña del navegador
st.set_page_config(page_title="JAHORI - Discover Your Blind Spots", page_icon="🔮", layout="centered")

# 2. Inyección de Estilo CSS Corporativo
st.markdown("""
    <style>
    /* Fondo blanco limpio estilo Google */
    .stApp { background-color: #FFFFFF; }
    
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .compliance-box { background-color: #F1F3F9; border-left: 4px solid #3E63DD; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    
    /* CSS ISOLADO PARA LA HOME (Solo actúa si NO hay barra lateral) */
    .stApp:not(:has(div[data-testid="stSidebar"])) div[data-testid="stHorizontalBlock"] {
        display: flex !important; 
        flex-direction: row !important; 
        justify-content: center !important; 
        align-items: center !important; 
        gap: 20px !important; 
        width: 100% !important; 
        max-width: 400px !important; 
        margin: 25px auto 0 auto !important;
    }
    .stApp:not(:has(div[data-testid="stSidebar"])) div[data-testid="column"] {
        width: 50% !important; flex: 1 !important; display: flex !important; justify-content: center !important; align-items: center !important; padding: 0 !important; margin: 0 !important;
    }
    
    /* Diseño estándar para botones pequeños (Home, Login, Sign Up) */
    .stButton>button { 
        width: 160px !important; background-color: #3E63DD !important; color: white !important; border-radius: 20px !important; border: 1px solid #3E63DD !important; padding: 10px 20px !important; font-weight: 500 !important; font-size: 14.5px !important; cursor: pointer !important; box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important; margin-left: auto !important; margin-right: auto !important; display: block !important; white-space: nowrap !important;
    }
    .stButton>button:hover { background-color: #2E4cbd !important; border-color: #2E4cbd !important; }
    
    /* Ajuste para los botones con textos limpios y cortos */
    div.long-text-button .stButton>button {
        width: 100% !important;
        max-width: 200px !important;
        white-space: nowrap !important;
        display: block !important;
        margin: 15px auto !important;
    }
    
    /* REJILLA DE ADJETIVOS (2 COLUMNAS) */
    .stApp:has(div[data-testid="stSidebar"]) div[data-testid="stHorizontalBlock"] { 
        max-width: 100% !important; width: 100% !important; display: flex !important; flex-direction: row !important; gap: 15px !important; 
    }
    .stApp:has(div[data-testid="stSidebar"]) div[data-testid="stHorizontalBlock"] div[data-testid="column"] { 
        width: 50% !important; max-width: 50% !important; flex: 1 1 50% !important; 
    }
    
    div[data-testid="stCheckbox"] {
        background-color: #F8F9FA !important; padding: 10px 16px !important; border-radius: 10px !important; border: 1px solid #E4E7EB !important; margin-bottom: 10px !important; width: 100% !important; height: 50px !important; display: flex !important; align-items: center !important; transition: all 0.2s ease-in-out !important; box-sizing: border-box !important;
    }
    div[data-testid="stCheckbox"]:hover { background-color: #F1F3F9 !important; border-color: #3E63DD !important; }
    div[data-testid="stCheckbox"] label { display: flex !important; align-items: center !important; height: 100% !important; width: 100% !important; }
    div[data-testid="stCheckbox"] label p { color: #333333 !important; font-weight: 500 !important; font-size: 15px !important; white-space: nowrap !important; margin: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicialización de la Base de Datos SQLite
def init_db():
    conn = sqlite3.connect("reflex.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, share_token TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS self_assessment (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, adjectives TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, anonymous_adjectives TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ai_report (user_id INTEGER PRIMARY KEY, report_text TEXT)")
    conn.commit()
    return conn

conn = init_db()

JOHARI_ADJECTIVES = [
    "Able", "Accepting", "Adaptable", "Bold", "Brave", "Calm", "Caring", "Cheerful", "Clever", "Complex", 
    "Confident", "Dependable", "Dignified", "Empathetic", "Energetic", "Friendly", "Giving", "Happy", "Helpful", "Idealistic", 
    "Independent", "Ingenious", "Intelligent", "Introverted", "Kind", "Knowledgeable", "Logical", "Loving", "Mature", "Modest"
]
# ===================================================================================================
#    [JAHORI WINDOW EMBA SAAS - BLINDADO V11] - FLUJO PÚBLICO Y ACCESOS (PART 2)
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
        # 💡 FIX SEGURO: Extracción correcta del entero desde la tupla
        target_user_id = int(user_data[0])
        st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 42px;'><span style='color: #3E63DD;'>Evaluate Your</span> Friend</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666666; font-size: 16px;'>Your anonymous feedback is 100% confidential and RODO compliant.</p>", unsafe_allow_html=True)
        st.markdown("<div class='compliance-box'><strong>🔒 RODO Compliance Shield:</strong> Anonymous form. No tracking.</div>", unsafe_allow_html=True)
        
        st.write("Select 3 to 10 adjectives that best describe your colleague:")
        selected_friend_words = []
        cols = st.columns(2)
        for i, adj in enumerate(JOHARI_ADJECTIVES):
            with cols[i % 2]:
                st.checkbox(adj, key=f"friend_{adj}")
                if st.session_state.get(f"friend_{adj}"):
                    selected_friend_words.append(adj)
                    
        # 💡 TEXTO CORTO OPTIMIZADO: "Submit" impecable para móviles estrechos
        st.markdown("<div class='long-text-button'>", unsafe_allow_html=True)
        btn_submit_friend = st.button("Submit")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if btn_submit_friend:
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
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.expander("ℹ️ Learn more about the Johari Window framework", expanded=True):
                st.markdown("""
                    ### What is the Johari Window?
                    Developed by psychologists Joseph Luft and Harrington Ingham, the **Johari Window** is a cognitive psychological tool used to enhance self-awareness, interpersonal relationships, and leadership dynamics.
                """)
                    
        elif st.session_state.page == "Register":
            st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 36px;'><span style='color: #3E63DD;'>Create Your</span> Account</h1>", unsafe_allow_html=True)
            st.info("🔒 No email required. You can use any custom username and password.")
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
                        # 💡 FIX SEGURO: Extracción correcta del ID en el registro
                        st.session_state.user = int(user_data[0]) if user_data else None
                        st.session_state.page = "Dashboard"; st.rerun()
                    except sqlite3.IntegrityError: st.error("This username is already taken.")
                        
        elif st.session_state.page == "Login":
            st.markdown("<h1 style='text-align: center; font-weight: 700; color: #111111; font-size: 36px;'>Log <span style='color: #3E63DD;'>In</span></h1>", unsafe_allow_html=True)
            st.info("🔒 No email needed. Enter your configured nickname and password to access.")
            log_user = st.text_input("Username")
            log_pass = st.text_input("Password", type="password")
            if st.button("Sign In"):
                hashed = hashlib.sha256(log_pass.encode()).hexdigest()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM user WHERE username = ? AND password_hash = ?", (log_user, hashed))
                result = cursor.fetchone()
                if result:
                    # 💡 FIX SEGURO: Extracción correcta del ID en el inicio de sesión
                    st.session_state.user = int(result[0])
                    st.session_state.page = "Dashboard"; st.rerun()
                else: st.error("Incorrect username or password.")
                    
        if st.session_state.page != "Home":
            if st.button("⬅️ Back to Home"): st.session_state.page = "Home"; st.rerun()
# ===================================================================================================
#    [JAHORI WINDOW EMBA SAAS - BLINDADO V11] - WIZARD PANEL Y MATRIX GRID (PART 3)
# ===================================================================================================
    else:
        st.sidebar.markdown(f"### 🔒 Session Secure")
        if st.sidebar.button("🚪 Log Out"): st.session_state.user = None; st.session_state.page = "Home"; st.rerun()
            
        current_user_id = int(st.session_state.user)
        cursor = conn.cursor()
        
        cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (current_user_id,))
        has_self = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id = ?", (current_user_id,))
        f_count_data = cursor.fetchone()
        # 💡 FIX SEGURO DE LA LÍNEA SOLICITADA: Coloca los corchetes ceros estrictamente ADENTRO de la función int()
        f_count = int(f_count_data[0]) if f_count_data else 0
        
        cursor.execute("SELECT report_text FROM ai_report WHERE user_id = ?", (current_user_id,))
        saved_report = cursor.fetchone()
        
        st.markdown("<h1 style='font-size:28px; font-weight:700;'>Your Johari Control Panel</h1>", unsafe_allow_html=True)
        
        # Enrutamiento por pasos secuenciales (Wizard)
        if not has_self:
            current_step = "Step 1: Self Assessment"
        elif f_count < 3 and not saved_report:
            current_step = "Step 2: Link Distribution"
        else:
            current_step = "Step 3: Executive AI Matrix"
            
        if current_step == "Step 1: Self Assessment":
            st.subheader("🎯 Step 1: Complete Your Self Assessment")
            st.write("Select 3 to 10 adjectives that best describe you today:")
            selected_my_words = []
            cols = st.columns(2)
            for i, adj in enumerate(JOHARI_ADJECTIVES):
                with cols[i % 2]:
                    st.checkbox(adj, key=f"my_{adj}")
                    if st.session_state.get(f"my_{adj}"):
                        selected_my_words.append(adj)
                        
            # 💡 TEXTO CORTO OPTIMIZADO: "Next ➡️" para una usabilidad móvil perfecta
            st.markdown("<div class='long-text-button'>", unsafe_allow_html=True)
            btn_save_self = st.button("Next ➡️")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if btn_save_self:
                if len(selected_my_words) < 3 or len(selected_my_words) > 10:
                    st.error("Please select between 3 and 10 adjectives.")
                else:
                    my_str = ",".join(selected_my_words)
                    cursor.execute("INSERT OR REPLACE INTO self_assessment (user_id, adjectives) VALUES (?, ?)", (current_user_id, my_str))
                    conn.commit()
                    st.success("Your assessment has been saved! Moving forward...")
                    st.rerun()
                    
        elif current_step == "Step 2: Link Distribution":
            st.subheader("🔗 Step 2: Distribute Your Anonymous URL")
            st.warning(f"Waiting for feedback. You have received ({f_count}/3) evaluations so far.")
            st.write("Copy this secure link and share it with your EMBA network via WhatsApp or Slack:")
            
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
            st.info("💡 Once you receive at least 3 anonymous evaluations from your colleagues, this window will automatically unlock the AI coaching report button.")
            if st.button("🔄 Refresh Progress"): st.rerun()
                
        elif current_step == "Step 3: Executive AI Matrix":
            st.subheader("📊 Step 3: Your Personality Matrix & Leadership Plan")
            
            cursor.execute("SELECT adjectives FROM self_assessment WHERE user_id = ?", (current_user_id,))
            user_res = cursor.fetchone()
            user_set = set(user_res[0].split(",")) if user_res and user_res[0] else set()
            
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
            unknown_area = ["Undiscovered qualities left to explore."]
            
            open_html = "<br>".join(open_area) if open_area else "None"
            blind_html = "<br>".join(blind_area) if blind_area else "None"
            hidden_html = "<br>".join(hidden_area) if hidden_area else "None"
            unknown_html = "<br>".join(unknown_area)
            
            # MATRIZ HTML BLINDADA: Garantiza la alineación y colores sin romperse
            st.markdown(f"""
                <table style="width:100%; border-collapse: separate; border-spacing: 15px; font-family: -apple-system, sans-serif; table-layout: fixed;">
                    <tr>
                        <td style="width:50%; background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 16px; vertical-align: top;">
                            <div style="color: #1E40AF; font-weight: 700; margin-bottom: 12px; font-size: 16px;">👐 1. Open Area:</div>
                            <div style="color: #1E3A8A; font-weight: 500; font-size: 15px; line-height: 1.6;">{open_html}</div>
                        </td>
                        <td style="width:50%; background-color: #FEFCE8; border: 1px solid #FEF08A; border-radius: 8px; padding: 16px; vertical-align: top;">
                            <div style="color: #854D0E; font-weight: 700; margin-bottom: 12px; font-size: 16px;">👁️ 2. Blind Area:</div>
                            <div style="color: #713F12; font-weight: 500; font-size: 15px; line-height: 1.6;">{blind_html}</div>
                        </td>
                    </tr>
                    <tr>
                        <td style="width:50%; background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 16px; vertical-align: top;">
                            <div style="color: #991B1B; font-weight: 700; margin-bottom: 12px; font-size: 16px;">🔒 3. Hidden Area:</div>
                            <div style="color: #7F1D1D; font-weight: 500; font-size: 15px; line-height: 1.6;">{hidden_html}</div>
                        </td>
                        <td style="width:50%; background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 16px; vertical-align: top;">
                            <div style="color: #166534; font-weight: 700; margin-bottom: 12px; font-size: 16px;">🔮 4. Unknown Area:</div>
                            <div style="color: #14532D; font-weight: 500; font-size: 15px; line-height: 1.6;">{unknown_html}</div>
                        </td>
                    </tr>
                </table>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><h3 style='color: #3E63DD; font-weight: 700;'>🧠 Executive Coaching Report</h3>", unsafe_allow_html=True)
            
            if saved_report and saved_report[0]:
                st.write(saved_report[0])
                st.caption("🔒 *Your personalized Executive Report has been successfully recorded and saved in your secure profile.*")
            else:
                # 💡 TEXTO CORTO OPTIMIZADO: "Generate Report" limpio para el botón ejecutivo
                st.markdown("<div class='long-text-button'>", unsafe_allow_html=True)
                btn_generate_ai = st.button("Generate Report")
                st.markdown("</div>", unsafe_allow_html=True)
                
                if btn_generate_ai:
                    api_key = os.environ.get("GEMINI_API_KEY")
                    if not api_key: st.error("API Secret Key missing.")
                    else:
                        with st.spinner("Gemini is analyzing your psychological vectors..."):
                            try:
                                client = genai.Client(api_key=api_key)
                                prompt_payload = f"Act as an expert leadership coach specialized in the Johari Window model. My assessment: {', '.join(user_set)}. Peer reputation attributes: {', '.join(all_friends_list)}. Please write an analysis of my blind spots and an actionable plan in exactly two short prose paragraphs in English."
                                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_payload)
                                raw_text = response.text
                                
                                cursor.execute("INSERT OR REPLACE INTO ai_report (user_id, report_text) VALUES (?, ?)", (current_user_id, raw_text))
                                conn.commit()
                                st.write(raw_text)
                                st.success("Report successfully generated and locked!")
                                st.rerun()
				except Exception as e: st.error(f"Google GenAI Connection temporary suspended: {e}")