from abc import ABC, abstractmethod
from typing import Tuple, Any


class IVectorRepository(ABC):
    @abstractmethod
    async def add_vectors(self, source_id: str, file_path: str) -> Tuple[bool, int]:       
        pass
    
    @abstractmethod
    async def delete_vectors(self, source_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_retriever(self, source_id: str) -> Any:
        pass