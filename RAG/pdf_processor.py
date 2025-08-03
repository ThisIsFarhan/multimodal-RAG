import pymupdf
from PIL import Image
import base64
import io
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from RAG.utils import image_embedding, text_embedding
from langchain_community.vectorstores import FAISS

def pdf_upload(pdf_path):
    # Storage for all documents and embeddings
    all_docs = []
    all_embeddings = []
    image_data_store = {}  # Store actual image data for LLM

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    doc = pymupdf.open(pdf_path)

    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            temp_doc = Document(page_content=text, metadata={"page": i, "type":"text"})
            chunks = text_splitter.split_documents([temp_doc])
            
            for chunk in chunks:
                #create embeddings
                text_emb = text_embedding(chunk.page_content)
                all_embeddings.append(text_emb)
                all_docs.append(chunk)

        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image = base_image["image"]

            pil_image = Image.open(io.BytesIO(image)).convert("RGB")

            img_id = f"page{i}_img{img_idx}"

            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            image_data_store[img_id] = img_base64

            img_emb = image_embedding(pil_image)
            
            image_doc = Document(
                page_content=f"[Image: {img_id}]",
                metadata={"page": i, "type":"image" ,"image_id": img_id}
            )
            all_docs.append(image_doc)
            all_embeddings.append(img_emb)
    doc.close()



    return all_docs, all_embeddings, image_data_store