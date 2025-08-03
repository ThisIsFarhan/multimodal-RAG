from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

def llm_initiation(api):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api)
    return llm

def llm_inference(llm, results, img_store):
    txt_docs = [doc for doc in results if doc.metadata['type'] == 'text']
    img_docs = [doc.metadata for doc in results if doc.metadata['type'] == 'image']

    content = []
    text_context = []
    image_context = []


    if txt_docs:
        combined_txt = "\n\n".join([f"Page {doc.metadata["page"]}: {doc.page_content}" for doc in txt_docs])
        text_context.append(combined_txt)
        content.append({
            "type":"text",
            "text": combined_txt
        })


    if img_docs:
        for doc in img_docs:
            img_id = doc["image_id"]
            if img_id and img_id in img_store:
                content.append({
                    "type":"text",
                    "text": f"\nImage from page {doc["page"]}:\n"
                })

                content.append({
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{img_store[img_id]}"
                })
                image_context.append(img_store[img_id])

    content.append({
        "type": "text",
        "text": "\n\nPlease answer the question based on the provided text and images."
    })
    message = HumanMessage(content)
    response = llm.invoke([message])
    return response.content, text_context, image_context

# message_local = HumanMessage(
#     content=[
#         {"type": "text", "text": "Describe the local image."},
#         {"type": "image_url", "image_url": f"data:image/png;base64,{encoded_image}"},
#     ]
# )