from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
from schemas.query import QueryInput
from schemas.response import LLMResponse
from RAG.llm import llm_inference
from RAG.vector_db import populate_db, retrieve_docs
from RAG.pdf_processor import upload_pdf, split_text

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Multimodal RAG Application"}


@app.post("/query", response_model=LLMResponse)
def inference(query: QueryInput):
    # try:
        q = query.question
        related_docs = retrieve_docs(q)
        response = llm_inference(q, related_docs)
        return LLMResponse(
            response=response.content
        )
    # except:
    #     raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path = os.path.join("pdfs", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    pdf_data = upload_pdf(file_path)
    chunked = split_text(pdf_data)
    populate_db(chunked)

    return {"message": f"File ({file.filename}) uploaded successfully"}
