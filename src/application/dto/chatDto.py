from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class MessageDTO(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=5, description="Pergunta")
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    class Config:
        populate_by_name = True

class ChatInputDTO(BaseModel):
    source_id: str = Field(..., description="ID do documento")
    prompt: Optional[str] = Field(default=None, exclude=True, description="Prompt do modelo")
    temperature: Optional[float] = Field(default=None, exclude=True, description="Temperatura do modelo")
    messages: List[MessageDTO] = Field(..., min_length=1, description="Mensagens")
    
    class Config:
        populate_by_name = True

class ChatOutputDTO(BaseModel):
    content: str