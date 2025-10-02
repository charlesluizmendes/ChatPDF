from pydantic import BaseModel


class DeleteFileInputDTO(BaseModel):
    source_id: str