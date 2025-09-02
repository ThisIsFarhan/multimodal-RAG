import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""

load_dotenv()

# Validate API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is required")

model = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)

def llm_inference(question, documents):
    try:
        context = documents

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | model

        result = chain.invoke({"question": question, "context": context})
        logger.info(f"Successfully generated response for question: {question[:50]}...")
        return result

    except Exception as e:
        logger.error(f"Error during LLM inference: {e}")
        raise