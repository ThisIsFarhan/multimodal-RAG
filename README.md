# Multimodal RAG

A Multimodal Retrieval-Augmented Generation (RAG) application that enables users to upload PDFs, extract text and figures, and ask questions about the content. The system leverages advanced language models and the `unstructured` library for comprehensive document understanding and responses with relevant contextual image data. This system has been backed by Role Based Access Control (Backend) with user authentication.

[![Multimodal RAG Assistant - Watch Video](https://cdn.loom.com/sessions/thumbnails/82e55933dbde4ce1b1901c0ca51a48f0-7ea095cfe1762287-full-play.gif)](https://www.loom.com/share/82e55933dbde4ce1b1901c0ca51a48f0)

## Features

- **PDF Parsing:** Uses the [`unstructured`](https://github.com/Unstructured-IO/unstructured) library to extract text, figures, and tables from uploaded PDFs.
- **Figure Annotation:** Annotates extracted figures and tables using the `meta-llama/llama-4-scout-17b-16e-instruct` model for concise, single-paragraph summaries.
- **Text Embedding & Retrieval:** Stores and retrieves document chunks using vector embeddings (`sentence-transformers/all-mpnet-base-v2`) and weviate vector store.
- **Question Answering:** Generates concise answers to user queries using the `llama-3.1-8b-instant` model, grounded in retrieved document context.
- **Streamlit Frontend:** Simple web interface for uploading PDFs and asking questions.
- **FastAPI Backend:** RBAC API managing the endpoint access to both admin and users accordingly.
- **Auth:** Used MongoDB to store the user profiles for login.


## Models Used

- **Figure Annotation:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Response Generation:** `llama-3.1-8b-instant`

## Getting Started

1. **Install dependencies:**
   ```sh
   uv pip install -r requirements.txt
   ```
   Or use the dependencies listed in [pyproject.toml](pyproject.toml).

2. **Set up environment variables:**
   - Create a `.env` file with your GROQ API key:
     ```
     GROQ_API_KEY=your_groq_api_key
     WEAVIATE_API_KEY=your_weaviate_api_key_here
     WEAVIATE_URL=your_weaviate_cluster_url_here
     MONGO_URI=your_mongo_uri_here

     ```

3. **Run the backend:**
   ```sh
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

4. **Run the frontend:**
   ```sh
   streamlit run frontend/frontend.py
   ```

## Usage
- Login/signup as an admin or user
- admin can only upload pdf to the vector db.
- users can only questions about the document.
- The system will extract text and figures, annotate figures, and answer your questions using retrieved context.

## File Structure

- [`main.py`](main.py): FastAPI backend
- [`frontend/frontend.py`](frontend/frontend.py): Streamlit frontend
- [`RAG/pdf_processor.py`](RAG/pdf_processor.py): PDF parsing and figure annotation
- [`RAG/vector_db.py`](RAG/vector_db.py): Vector database for retrieval
- [`RAG/llm.py`](RAG/llm.py): LLM-based response generation
- [`schemas/query.py`](schemas/query.py), [`schemas/response.py`](schemas/response.py): Pydantic schemas


**Note:** This project requires access to GROQ API and the specified Llama
