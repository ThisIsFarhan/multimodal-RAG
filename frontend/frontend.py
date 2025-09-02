import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://127.0.0.1:8000"  # your FastAPI server

st.set_page_config(page_title="Multimodal RAG App", layout="centered")

st.title("📚 Multimodal RAG App")
st.write("Upload PDFs and ask questions from them.")

# --- Upload PDF Section ---
st.header("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Upload"):
        try:
            with st.spinner("Uploading and processing PDF..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/uploadfile", files=files, timeout=300)

            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                error_detail = response.json().get("detail", "Unknown error occurred")
                st.error(f"Error: {error_detail}")
                logger.error(f"Upload error: {error_detail}")
        except requests.exceptions.Timeout:
            st.error("Upload timed out. Please try again with a smaller file.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend server. Please ensure it's running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logger.error(f"Upload exception: {e}")

st.markdown("---")

# --- Query Section ---
st.header("Ask a Question")
query_text = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if query_text.strip() == "":
        st.warning("Please enter a question first.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{BACKEND_URL}/query",
                    json={"question": query_text},
                    timeout=60
                )
            if response.status_code == 200:
                st.success("✅ Answer:")
                st.write(response.json()["response"])
            else:
                error_detail = response.json().get("detail", "Unknown error occurred")
                st.error(f"Error: {error_detail}")
                logger.error(f"Query error: {error_detail}")
        except requests.exceptions.Timeout:
            st.error("Query timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend server. Please ensure it's running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logger.error(f"Query exception: {e}")
