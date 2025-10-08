from typing import Any
from pydantic import BaseModel


class AddFileInputDTO(BaseModel):
    file: Any
    
    class Config:
        arbitrary_types_allowed = True

class AddFileOutputDTO(BaseModel):
    source_id: str