from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
import logging
from schemas.query import QueryInput
from schemas.response import LLMResponse
from RAG.llm import llm_inference
from RAG.vector_db import populate_db, retrieve_docs
from RAG.pdf_processor import upload_pdf, split_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Ensure required directories exist
UPLOAD_DIR = "pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Multimodal RAG Application"}


# @app.post("/query", response_model=LLMResponse)
# def inference(query: QueryInput):
#     try:
#         q = query.question
#         if not q.strip():
#             raise HTTPException(status_code=400, detail="Question cannot be empty.")

#         related_docs = retrieve_docs(q)
#         response = llm_inference(q, related_docs)
#         return LLMResponse(
#             response=response.content
#         )
#     except ValueError as e:
#         logger.error(f"Vector store error: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logger.error(f"Error during inference: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/query", response_model=LLMResponse)
def inference(query: QueryInput):
    try:
        q = query.question.strip()
        if not q:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # Retrieve both text and image-caption docs
        related_docs = retrieve_docs(q)

        # Separate into text + images
        text_contexts = []
        image_contexts = []
        image_paths = []

        for doc in related_docs:
            if doc.get("type") == "image":
                caption = doc["content"]
                path = doc.get("image_path")
                image_contexts.append(caption)
                image_paths.append(path)
            else:
                text_contexts.append(doc["content"])

        # Merge text + image contexts for the LLM
        full_context = "\n\n".join(text_contexts + image_contexts)

        # Pass to LLM
        response = llm_inference(q, full_context)

        return LLMResponse(
            response=response.content,
            images=image_paths
        )

    except ValueError as e:
        logger.error(f"Vector store error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(file.filename)
        if not safe_filename or safe_filename == "." or safe_filename == "..":
            raise HTTPException(status_code=400, detail="Invalid filename.")

        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process PDF
        pdf_data = upload_pdf(file_path)
        # chunked = split_text(pdf_data)
        populate_db(pdf_data)

        logger.info(f"Successfully processed file: {safe_filename}")
        return {"message": f"File ({safe_filename}) uploaded successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Error processing file.")
