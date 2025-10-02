from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.pdf import Pdf


class IPdfRepository(ABC):
    @abstractmethod
    async def add(self, document: Pdf) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, source_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_by_id(self, source_id: str) -> Optional[Pdf]:
        pass
    
    @abstractmethod
    async def exists(self, source_id: str) -> bool:
        pass