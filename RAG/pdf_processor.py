import base64
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.utils.constants import PartitionStrategy
import os
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

figure_dir = "./figures/"

def extract_text(file_path):
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
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    return chat_completion.choices[0].message.content

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def upload_pdf(file_path):
    elements = partition_pdf(
            file_path,
            strategy=PartitionStrategy.HI_RES,
            extract_image_block_types=["Image", "Table"],
            extract_image_block_output_dir=figure_dir
        )

    text_elements = [element.text for element in elements if element.category not in ["Image", "Table"]]

    for file in os.listdir(figure_dir):
            extracted_text = extract_text(figure_dir + file)
            text_elements.append(extracted_text)

    text_elements = "\n\n".join(text_elements)

    return text_elements

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )

    return text_splitter.split_text(text)