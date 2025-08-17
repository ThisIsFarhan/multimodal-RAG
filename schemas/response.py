from pydantic import BaseModel, Field
from typing import List, Optional

class LLMResponse(BaseModel):
    response: str = Field(..., description="LLM-generated answer to the query")
    