from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = InMemoryVectorStore(embedding=embeddings)

def populate_db(all_docs):
    vector_store.add_texts(all_docs)

def retrieve_docs(query, k=5):
    if vector_store is None:
        raise ValueError("Vector store is not initialized. Please populate the database first.")
    results = vector_store.similarity_search(
        query=query,
        k=k
    )
    return results