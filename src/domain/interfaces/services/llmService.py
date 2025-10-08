from abc import ABC, abstractmethod


class IllmService(ABC):
    @abstractmethod
    async def ask(self, messages: list, retriever, prompt: str, temperature: float) -> str:
        pass