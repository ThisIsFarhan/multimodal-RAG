import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# App config
st.set_page_config(page_title="Multi-Modal RAG", layout="centered")
st.title("🧠 Gemini-powered Multi-Modal RAG")

# Session state setup
if "llm_initialized" not in st.session_state:
    st.session_state.llm_initialized = False
if "api_key" not in st.session_state:
    st.session_state.api_key = None

# Step 1: Enter API key and initialize LLM
if not st.session_state.llm_initialized:
    with st.form("init_llm_form"):
        api_key = st.text_input("🔐 Enter your Gemini API key", type="password")
        submitted = st.form_submit_button("Initialize LLM")

        if submitted:
            if api_key:
                payload = {"api_key": api_key}
                with st.spinner("🔄 Initializing Gemini model..."):
                    res = requests.post("http://localhost:8000/initiate_model", json=payload)
                if res.status_code == 200:
                    st.success("✅ LLM initialized successfully!")
                    st.session_state.llm_initialized = True
                    st.session_state.api_key = api_key
                else:
                    st.error(f"❌ Initialization failed: {res.text}")
            else:
                st.warning("⚠️ Please enter a valid API key.")

# Step 2: Upload and Query
if st.session_state.llm_initialized:
    st.markdown("---")
    st.subheader("📤 Upload PDF")

    uploaded_file = st.file_uploader("Select a PDF", type=["pdf"])
    if uploaded_file:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }
        with st.spinner("Uploading file..."):
            res = requests.post("http://localhost:8000/uploadfile", files=files)
        if res.status_code == 200:
            st.success("✅ File uploaded and processed!")
        else:
            st.error(f"❌ Upload failed: {res.text}")

    st.markdown("---")
    st.subheader("💬 Ask a Question")

    with st.form("query_form"):
        query = st.text_input("Your question:")
        submit_query = st.form_submit_button("Submit Query")

        if submit_query:
            if query:
                res = requests.post("http://localhost:8000/query", json={"question": query})
                if res.status_code == 200:
                    response = res.json()

                    # Show image contexts
                    if response.get("image_contexts"):
                        st.markdown("### 🖼️ Retrieved Image Contexts:")
                        for i, img_str in enumerate(response["image_contexts"]):
                            try:
                                img_data = base64.b64decode(img_str)
                                image = Image.open(BytesIO(img_data))
                                st.image(image, caption=f"Context Image {i + 1}", use_container_width=True)
                            except Exception as e:
                                st.warning(f"⚠️ Failed to load image {i + 1}: {e}")

                    # Show response
                    st.markdown("### 🤖 Response:")
                    st.write(response["response"])
                else:
                    st.error(f"❌ Query failed: {res.text}")
            else:
                st.warning("⚠️ Enter a question before submitting.")
