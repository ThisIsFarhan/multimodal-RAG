from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import shutil
import logging
from schemas.query import QueryInput
from schemas.response import LLMResponse
from schemas.signup import SignUp

from RAG.llm import llm_inference
from RAG.vector_db import populate_db, retrieve_docs
from RAG.pdf_processor import upload_pdf, split_text
from auth.db import users_collection
from auth.utils import verify_password, hash_password
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
security = HTTPBasic()

# Ensure required directories exist
UPLOAD_DIR = "pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def authenticate(credentials:HTTPBasicCredentials=Depends(security)):
    user=users_collection.find_one({"username":credentials.username})
    if not user or not verify_password(credentials.password,user['password']):
        raise HTTPException(status_code=401,details="Invalid credentials")
    return {"username":user["username"],"role":user["role"]}

def admin_check(user=Depends(authenticate)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user

def user_check(user=Depends(authenticate)):
    if user["role"] != "user":
        raise HTTPException(status_code=403, detail="Users only")
    return user

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/")
def home():
    return {"message": "Multimodal RAG Application"}


@app.post("/signup")
def signup(req:SignUp):
    if users_collection.find_one({"username":req.username}):
        raise HTTPException(status_code=400,details="User already exists")
    users_collection.insert_one({
        "username":req.username,
        "password":hash_password(req.password),
        "role":req.role
    })
    return {"message":"User created successfully"}

@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message":f"Welcome {user['username']}","role":user["role"]}


@app.post("/query", response_model=LLMResponse)
def inference(query: QueryInput, user=Depends(user_check)):
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
async def create_upload_file(file: UploadFile = File(...), user=Depends(admin_check)):
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(file.filename)
        if not safe_filename or safe_filename == "." or safe_filename == "..":
            raise HTTPException(status_code=400, detail="Invalid filename.")
        
        # Remove existing PDF if present
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith(".pdf"):
                os.remove(os.path.join(UPLOAD_DIR, f))

        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process PDF
        pdf_data = upload_pdf(file_path)
        populate_db(pdf_data)

        logger.info(f"Successfully processed file: {safe_filename}")
        return {"message": f"File ({safe_filename}) uploaded successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Error processing file.")
