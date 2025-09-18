import logging
from langchain_huggingface import HuggingFaceEmbeddings
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter
from langchain_weaviate.vectorstores import WeaviateVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
weaviate_api_key = os.getenv("WEVIATE_API_KEY")
weaviate_url = os.getenv("WEVIATE_URL")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate environment variables
if not weaviate_api_key:
    raise ValueError("WEVIATE_API_KEY environment variable is required")
if not weaviate_url:
    raise ValueError("WEVIATE_URL environment variable is required")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)
vector_store = WeaviateVectorStore(
    client=client,
    index_name="Documents",   # schema name, Weaviate will create if missing
    text_key="content",       # text field to store your document body
    embedding=embeddings
)

def populate_db(all_docs):
    try:
        if not all_docs:
            raise ValueError("No documents provided to populate the database.")

        collection = client.collections.get("Documents")
        collection.data.delete_many(
            where=Filter.by_property("content").like("*")
        )
        logger.info(f"Successfully cleared vector store")
        texts = [doc.page_content for doc in all_docs]
        metadatas = [doc.metadata for doc in all_docs]

        vector_store.add_texts(texts, metadatas=metadatas)
        logger.info(f"Successfully added {len(all_docs)} documents to vector store")
    except Exception as e:
        logger.error(f"Error populating database: {e}", exc_info=True)
        raise

def retrieve_docs(query, k=5):
    try:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        results = vector_store.similarity_search(
            query=query,
            k=k
        )

        if not results:
            logger.warning(f"No similar documents found for query: {query}")

        final_results = []
        for r in results:
            if r.metadata.get("type") == "image":
                final_results.append({
                    "content": r.page_content,
                    "image_path": r.metadata.get("path"),
                    "type": "image"
                })
            else:
                final_results.append({
                    "content": r.page_content,
                    "type": "text"
                })

        return final_results

    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise