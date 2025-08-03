from langchain_community.vectorstores import FAISS
import numpy as np

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

vector_store = None

def populate_db(all_docs, all_embeddings):

    global vector_store
    
    embeddings_array = np.array(all_embeddings)

    vector_store = FAISS.from_embeddings(
        text_embeddings=[(doc.page_content, emb) for doc, emb in zip(all_docs, embeddings_array)],
        embedding=None,  # We're using precomputed embeddings
        metadatas=[doc.metadata for doc in all_docs]
    )


def retrieve_docs(query_embedding, k=5):
    if vector_store is None:
        raise ValueError("Vector store is not initialized. Please populate the database first.")
    results = vector_store.similarity_search_by_vector(
        embedding=query_embedding,
        k=5
    )
    return results