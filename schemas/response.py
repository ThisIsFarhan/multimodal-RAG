from pydantic import BaseModel, Field
from typing import List

class LLMResponse(BaseModel):
    response: str = Field(..., description="LLM-generated answer to the query")
    images: List[str] = Field(..., description="List of image paths related to the query")
