from src.domain.common.result import Result
from src.domain.interfaces.repositories.pdfRepository import IPdfRepository
from src.domain.interfaces.repositories.vectorRepository import IVectorRepository
from src.domain.interfaces.services.llmService import IllmService
from src.application.interfaces.chatService import IChatService
from src.application.dto.chatDto import ChatInputDTO, ChatOutputDTO


class ChatService(IChatService):
    def __init__(
        self,
        pdf_repository: IPdfRepository,
        vector_repository: IVectorRepository,
        llm_service: IllmService
    ):
        self.pdf_repository = pdf_repository
        self.vector_repository = vector_repository
        self.llm_service = llm_service

        self.default_prompt = (
            "Você é um assistente especializado em responder perguntas sobre documentos PDF. "
            "Use somente o contexto fornecido para responder de forma precisa e concisa."
            "Se a informação não estiver no contexto responda apenas 'Não possuo informações sobre isso.'"
        )
        self.default_temperature = 0.0

    async def message(self, dto: ChatInputDTO) -> Result[ChatOutputDTO]:
        exists = await self.pdf_repository.exists(dto.source_id)
        if not exists:
            return Result.error("Documento não encontrado")
        
        retriever = await self.vector_repository.get_retriever(dto.source_id)       

        prompt = dto.prompt if dto.prompt is not None else self.default_prompt
        temperature = dto.temperature if dto.temperature is not None else self.default_temperature

        content = await self.llm_service.ask(
            message=dto.message,
            retriever=retriever,
            prompt=prompt,
            temperature=temperature
        )
        
        output = ChatOutputDTO(content=content)        
        return Result.ok(data=output)