import streamlit as st
import requests
import logging
import os
from PIL import Image
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://127.0.0.1:8000/"
FIGURES_PATH = "../"

# Page config
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS (Dark Mode + Neon Accent) ==================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body, .main {
        font-family: 'Inter', sans-serif;
        background-color: #0f1117;
        color: #e2e8f0;
    }
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #f8fafc;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .glass-card {
        background: rgba(32, 34, 50, 0.9);
        backdrop-filter: blur(8px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(99,102,241,0.3);
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
        margin: 1.5rem 0;
    }
    .answer-box {
        background: #1a1c2c;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #6366f1;
        color: #e5e7eb;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 15px rgba(99,102,241,0.4);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139,92,246,0.6);
    }
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
    }
    .image-item img {
        border-radius: 12px;
        border: 2px solid #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# ================== Session State ==================
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "password" not in st.session_state:
    st.session_state.password = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# ================== Auth Pages ==================
def login_page():
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Signup"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                resp = requests.get(f"{BACKEND_URL}/login", auth=(username, password))
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.username = username
                    st.session_state.password = password
                    st.session_state.role = data["role"]
                    st.success(f"Welcome {username} ({data['role']})")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

    with tab2:
        st.subheader("Signup")
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        role = st.selectbox("Role", ["user", "admin"], key="signup_role")
        if st.button("Signup"):
            try:
                payload = {"username": new_user, "password": new_pass, "role": role}
                resp = requests.post(f"{BACKEND_URL}/signup", json=payload)
                if resp.status_code == 200:
                    st.success("✅ User registered! Please login now.")
                else:
                    st.error(resp.json().get("detail", "Signup failed"))
            except Exception as e:
                st.error(f"Signup error: {str(e)}")

# ================== Admin Page ==================
def admin_page():
    st.markdown('<div class="glass-card"><h2>📄 Upload PDF</h2></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file and st.button("🚀 Upload and Process"):
        with st.spinner("Processing..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            resp = requests.post(
                f"{BACKEND_URL}/uploadfile",
                files=files,
                auth=(st.session_state.username, st.session_state.password)
            )
            if resp.status_code == 200:
                st.success(resp.json()["message"])
            else:
                st.error(resp.json().get("detail", "Upload failed"))

# ================== User Page ==================
def user_page():
    st.markdown('<div class="glass-card"><h2>💬 Query Documents</h2></div>', unsafe_allow_html=True)
    query_text = st.text_area("Ask a question:", height=100)
    show_images = st.checkbox("Show reference images", value=True)

    if st.button("🔍 Get Answer"):
        if not query_text.strip():
            st.warning("Enter a question first")
        else:
            with st.spinner("Thinking..."):
                resp = requests.post(
                    f"{BACKEND_URL}/query",
                    json={"question": query_text},
                    auth=(st.session_state.username, st.session_state.password)
                )

                if resp.status_code == 200:
                    result = resp.json()
                    st.markdown("### ✨ Answer")
                    st.markdown(f'<div class="answer-box">{result["response"]}</div>', unsafe_allow_html=True)

                    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    FIGURES_PATH = os.path.join(PROJECT_ROOT, "figures")

                    if show_images and result.get("images"):
                        st.markdown("### 🖼️ Related Images")
                        cols = st.columns(3)
                        for idx, img_path in enumerate(result["images"][:6]):
                            filename = os.path.basename(img_path)
                            full_path = os.path.join(FIGURES_PATH, filename)
                            print("Resolved path:", full_path)
                            # print(img_path)
                            if os.path.exists(full_path):
                                with cols[idx % 3]:
                                    try:
                                        img = Image.open(full_path)
                                        st.image(img, caption=f"Figure {idx+1}", width=250)
                                    except:
                                        st.warning("⚠️ Could not load image")
                else:
                    st.error(resp.json().get("detail", "Query failed"))

# ================== Main ==================
st.markdown('<div class="main-header"><h1>🤖 Multimodal RAG Assistant</h1></div>', unsafe_allow_html=True)

if not st.session_state.username:
    login_page()
else:
    st.sidebar.write(f"👤 {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("🚪 Sign Out"):
        for k in ["username", "role", "password", "query_history"]:
            st.session_state[k] = None if k != "query_history" else []
        st.rerun()

    if st.session_state.role == "admin":
        admin_page()
    else:
        user_page()
