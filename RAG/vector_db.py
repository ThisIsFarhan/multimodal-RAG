import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = InMemoryVectorStore(embedding=embeddings)

def populate_db(all_docs):
    try:
        if not all_docs:
            raise ValueError("No documents provided to populate the database.")
        
        texts = [doc.page_content for doc in all_docs]
        metadatas = [doc.metadata for doc in all_docs]

        vector_store.add_texts(texts, metadatas=metadatas)
        logger.info(f"Successfully added {len(all_docs)} documents to vector store")
        # vector_store.add_texts(all_docs)
        # logger.info(f"Successfully added {len(all_docs)} documents to vector store")
    except Exception as e:
        logger.error(f"Error populating database: {e}")
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