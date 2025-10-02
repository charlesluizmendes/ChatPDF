from pydantic import BaseModel
from typing import Any


class AddFileInputDTO(BaseModel):
    file: Any
    
    class Config:
        arbitrary_types_allowed = True

class AddFileOutputDTO(BaseModel):
    source_id: str