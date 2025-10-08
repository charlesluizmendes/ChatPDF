from abc import ABC, abstractmethod


class IllmService(ABC):
    @abstractmethod
    async def ask(self, message: str, retriever, prompt: str, temperature: float) -> str:
        pass