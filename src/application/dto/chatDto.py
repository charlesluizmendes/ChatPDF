from pydantic import BaseModel, Field


class ChatInputDTO(BaseModel):
    source_id: str = Field(..., description="ID do documento")
    message: str = Field(..., min_length=1, description="Pergunta")

class ChatOutputDTO(BaseModel):
    content: str