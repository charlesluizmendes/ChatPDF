from pydantic import BaseModel, Field


class DeleteFileInputDTO(BaseModel):
    source_id: str = Field(..., description="ID do documento")