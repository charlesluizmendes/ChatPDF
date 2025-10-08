from typing import Optional
from pydantic import BaseModel, Field


class ChatInputDTO(BaseModel):
    source_id: str = Field(..., description="ID do documento")
    prompt: Optional[str] = Field(default=None, exclude=True, description="Prompt do modelo")
    temperature: Optional[float] = Field(default=None, exclude=True, description="Temperatura do modelo")
    message: str = Field(..., min_length=5, description="Pergunta")

class ChatOutputDTO(BaseModel):
    content: str