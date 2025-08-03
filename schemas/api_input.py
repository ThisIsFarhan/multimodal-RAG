from pydantic import BaseModel, Field

class APIKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=10, description="Your Gemini API key")
