# Multimodal RAG

A Multimodal Retrieval-Augmented Generation (RAG) application that enables users to upload PDFs, extract text and figures, and ask questions about the content. The system leverages advanced language models and the `unstructured` library for comprehensive document understanding.

## Features

- **PDF Parsing:** Uses the [`unstructured`](https://github.com/Unstructured-IO/unstructured) library to extract text, figures, and tables from uploaded PDFs.
- **Figure Annotation:** Annotates extracted figures and tables using the `meta-llama/llama-4-scout-17b-16e-instruct` model for concise, single-paragraph summaries.
- **Text Embedding & Retrieval:** Stores and retrieves document chunks using vector embeddings (`sentence-transformers/all-mpnet-base-v2`) and an in-memory vector store.
- **Question Answering:** Generates concise answers to user queries using the `llama-3.1-8b-instant` model, grounded in retrieved document context.
- **Streamlit Frontend:** Simple web interface for uploading PDFs and asking questions.

## Architecture

- **Backend:** FastAPI server ([main.py](main.py)) handles PDF uploads, document processing, and question answering.
- **Frontend:** Streamlit app ([frontend/frontend.py](frontend/frontend.py)) for user interaction.
- **PDF Processing:** [`RAG/pdf_processor.py`](RAG/pdf_processor.py) parses PDFs, extracts figures, and annotates them.
- **Vector Database:** [`RAG/vector_db.py`](RAG/vector_db.py) manages document chunk embeddings and similarity search.
- **LLM Inference:** [`RAG/llm.py`](RAG/llm.py) generates answers using context retrieved from the vector database.

## Models Used

- **Figure Annotation:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Response Generation:** `llama-3.1-8b-instant`

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   Or use the dependencies listed in [pyproject.toml](pyproject.toml).

2. **Set up environment variables:**
   - Create a `.env` file with your GROQ API key:
     ```
     GROQ_API_KEY=your_groq_api_key
     ```

3. **Run the backend:**
   ```sh
   uvicorn main:app --reload
   ```

4. **Run the frontend:**
   ```sh
   streamlit run frontend/frontend.py
   ```

## Usage

- Upload a PDF via the web interface.
- Ask questions about the document.
- The system will extract text and figures, annotate figures, and answer your questions using retrieved context.

## File Structure

- [`main.py`](main.py): FastAPI backend
- [`frontend/frontend.py`](frontend/frontend.py): Streamlit frontend
- [`RAG/pdf_processor.py`](RAG/pdf_processor.py): PDF parsing and figure annotation
- [`RAG/vector_db.py`](RAG/vector_db.py): Vector database for retrieval
- [`RAG/llm.py`](RAG/llm.py): LLM-based response generation
- [`schemas/query.py`](schemas/query.py), [`schemas/response.py`](schemas/response.py): Pydantic schemas


**Note:** This project requires access to GROQ API and the specified Llama
