import base64
import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.utils.constants import PartitionStrategy
from dotenv import load_dotenv
from groq import Groq
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Validate API key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is required")

client = Groq(api_key=api_key)

figure_dir = "./figures/"
# Ensure figures directory exists
os.makedirs(figure_dir, exist_ok=True)

def extract_text(file_path):
    try:
        # Getting the base64 string
        base64_image = encode_image(file_path)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Elaborate the findings in the image concisely in a single paragraph. Do not add anything."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Updated to a valid model name
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {e}")
        return f"[Error processing image: {os.path.basename(file_path)}]"

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        raise

def upload_pdf(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        elements = partition_pdf(
                file_path,
                strategy=PartitionStrategy.HI_RES,
                extract_image_block_types=["Image", "Table"],
                extract_image_block_output_dir=figure_dir
            )

        #Processing Text
        text_elements = [element.text for element in elements if element.category not in ["Image", "Table"]]
        text_elements = "\n\n".join(text_elements)
        text_docs = split_text(text_elements)

        # Process extracted figures if any exist
        image_docs = []
        if os.path.exists(figure_dir) and os.listdir(figure_dir):
            for file in os.listdir(figure_dir):
                file_path_full = os.path.join(figure_dir, file)
                if os.path.isfile(file_path_full):
                    extracted_text = extract_text(file_path_full)
                    image_docs.append(Document(
                        page_content=extracted_text,
                        metadata={"type": "image", "path": file_path_full}
                    ))

        
        return text_docs + image_docs

    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        raise

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    ) 
    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"type": "text"}) for chunk in chunks]

    # return text_splitter.split_text(text)