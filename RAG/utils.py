from transformers import CLIPProcessor, CLIPModel
import torch
import numpy

### initialize the Clip Model for unified embeddings
clip_model=CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor=CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

def image_embedding(image_data):
    inputs = clip_processor(images=image_data, return_tensors="pt")
    with torch.no_grad():
        output = clip_model.get_image_features(**inputs)
        output = output / output.norm(dim=-1, keepdim=True)
        return output.squeeze().numpy()
    
def text_embedding(text):
    inputs = clip_processor(
        text=text, 
        return_tensors="pt", 
        padding=True,
        truncation=True,
        max_length=77  # CLIP's max token length
    )
    with torch.no_grad():
        features = clip_model.get_text_features(**inputs)
        # Normalize embeddings
        features = features / features.norm(dim=-1, keepdim=True)
        return features.squeeze().numpy()