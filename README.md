# jahori-emba
An AI-powered executive platform based on the Johari Window framework to discover leadership blind spots. Integrated with Google Gemini 2.5 Flash to automatically generate customized corporate coaching reports and execution action plans. 

# JAHORI - AI-Powered Professional Leadership Analysis 🔮

An executive, minimal, and secure web application based on the psychological framework of the **Johari Window** (developed by Joseph Luft and Harrington Ingham). This platform maps a user’s internal self-perception against external anonymous peer feedback to identify professional blind spots and accelerate leadership growth.

🚀 **Built with Python, Streamlit, SQLite, and Google Gemini AI.**

---

## 🌟 Key Features

*   **Premium Minimalist UI:** Executive, clean, and balanced interface inspired by Google’s aesthetic. Designed with a corporate dark black and sapphire blue palette.
*   **100% RODO / RGPD Compliant Shield:** Strictly pseudo-anonymous. No email addresses, corporate identities, real names, or IP tracking. Accounts are managed via customized nicknames and encrypted passwords.
*   **Anti-IDOR Cryptographic Security:** Direct Object Reference vulnerabilities are completely mitigated by replacing sequential numeric database IDs with cryptographically unique **UUID v4 access tokens** in the public evaluation links. Peers cannot guess or sabotage other users' URLs.
*   **Google Gemini 2.5 Flash Pipeline:** Once a user receives a minimum threshold of 3 peer evaluations, an automated coaching engine analyzes the behavioral data vectors and delivers an immediate two-paragraph Executive Coaching Report and a personal Action Plan.

---

## 🛠️ Technology Stack

*   **Frontend & Layout:** Streamlit Core (Tailored CSS components).
*   **Database Management:** Native Python SQLite3 Engine.
*   **Artificial Intelligence:** Official `google-genai` Python SDK.
*   **Cryptography:** SHA-256 for password hashing & UUID v4 for link enmasking.

---

## 💻 Local Installation & Development

To test or run this SaaS application locally on your machine, follow these instructions:

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd jahori-emba
   ```

2. **Install required dependencies:**
   ```bash
   pip install streamlit google-genai
   ```

3. **Configure your Local Environment Secrets:**
   Set up your Google AI Studio token into your operating system memory before launching:
   ```bash
   # On Windows (cmd)
   set GEMINI_API_KEY=AIzaSyD_your_real_google_api_key
   ```

4. **Launch the application:**
   ```bash
   python -m streamlit run app.py
   ```
   Open your browser and navigate to `http://localhost:8501`.

---

## 🚀 Cloud Deployment (Streamlit Community Cloud)

This app is production-ready for automated serverless hosting on **Streamlit Cloud**:

1. Connect your **GitHub** account to [Streamlit Share](https://streamlit.io).
2. Select this repository (`jahori-emba`), target the `main` branch, and define `app.py` as the main entry point.
3. Open **Advanced Settings > Secrets** and paste your secure Google Gemini API token:
   ```text
   GEMINI_API_KEY = "AIzaSyD_your_real_google_api_key"
   ```
4. Click **Deploy!** Your scalable SaaS will be live in 60 seconds.

---

## ⚖️ License & Confidentiality

Distributed under the MIT License. See `LICENSE` for more information. All aggregated peer datasets are fragmented and non-traceable to ensure absolute data privacy and confidentiality rules.

