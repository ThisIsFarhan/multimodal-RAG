from pydantic import BaseModel, Field
from typing import List, Optional

class LLMResponse(BaseModel):
    response: str = Field(..., description="LLM-generated answer to the query")
    image_contexts: Optional[List[str]] = Field(
        default=None, description="Image contexts retrieved (base64)"
    )
    text_contexts: Optional[List[str]] = Field(
        default=None, description="Top-k relevant text chunks retrieved from the document"
    )