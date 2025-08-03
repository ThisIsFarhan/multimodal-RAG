from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from RAG.pdf_processor import pdf_upload
from schemas.api_input import APIKeyRequest
from schemas.query import QueryInput
from schemas.response import LLMResponse
from RAG.llm import llm_initiation, llm_inference
from RAG.vector_db import populate_db, retrieve_docs
from RAG.utils import text_embedding

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

all_docs = None
all_embeddings = None
image_store = None
llm_state = {"is_loaded" : False, "model" : None}

@app.get("/")
def home():
    return {"message": "Multimodal RAG Application"}

@app.post("/initiate_model")
def initiate_model(key:APIKeyRequest):
    global llm_state
    try:
        llm = llm_initiation(key.api_key)
        llm_state["is_loaded"] = True
        llm_state["model"] = llm
        return {"message": "Model intiated successfully"}
    except:
        raise HTTPException(status_code=500, detail="Failed to initialize model.")

@app.post("/query", response_model=LLMResponse)
def inference(query: QueryInput):
    try:
        q_emb = text_embedding(query.question)
        retrieved = retrieve_docs(q_emb)
        response, txt_ctx, img_ctx = llm_inference(llm_state["model"], retrieved, image_store)
        return LLMResponse(
            response=response,
            image_contexts=img_ctx,
            text_contexts=txt_ctx
        )
    except:
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path = os.path.join("pdfs", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    global all_docs, all_embeddings, image_store

    all_docs, all_embeddings, image_store = pdf_upload(file_path)
    populate_db(all_docs, all_embeddings)

    return {"message": f"File ({file.filename}) uploaded successfully"}
