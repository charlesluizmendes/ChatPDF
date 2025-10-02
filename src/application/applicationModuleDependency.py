from dotenv import load_dotenv

from src.infrastructure.infrastructureModuleDependency import (
    get_pdf_repository,
    get_vector_repository,
    get_llm_service
)
from src.application.services.sourceService import SourceService
from src.application.services.chatService import ChatService

load_dotenv(override=True)


def get_source_service() -> SourceService:
    return SourceService(
        pdf_repository=get_pdf_repository(),
        vector_repository=get_vector_repository()
    )

def get_chat_service() -> ChatService:
    return ChatService(
        pdf_repository=get_pdf_repository(),
        vector_repository=get_vector_repository(),
        llm_service=get_llm_service()
    )