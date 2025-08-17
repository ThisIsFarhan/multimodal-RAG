import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # your FastAPI server

st.set_page_config(page_title="Multimodal RAG App", layout="centered")

st.title("📚 Multimodal RAG App")
st.write("Upload PDFs and ask questions from them.")

# --- Upload PDF Section ---
st.header("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Upload"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/uploadfile", files=files)

        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(f"Error: {response.json()['detail']}")

st.markdown("---")

# --- Query Section ---
st.header("Ask a Question")
query_text = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if query_text.strip() == "":
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"question": query_text}
            )
        if response.status_code == 200:
            st.success("✅ Answer:")
            st.write(response.json()["response"])
        else:
            st.error("Error while fetching response.")
