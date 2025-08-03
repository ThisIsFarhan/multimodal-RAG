from pydantic import BaseModel, Field

class QueryInput(BaseModel):
    question: str = Field(..., description="User query")
