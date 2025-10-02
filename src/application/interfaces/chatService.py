from abc import ABC, abstractmethod

from src.domain.common.result import Result
from src.application.dto.chatDto import ChatInputDTO, ChatOutputDTO


class IChatService(ABC):
    @abstractmethod
    async def message(self, dto: ChatInputDTO) -> Result[ChatOutputDTO]:
        pass