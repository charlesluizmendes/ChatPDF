from fastapi import APIRouter, HTTPException, Depends

from src.domain.common.result import Result
from src.application.interfaces.chatService import IChatService
from src.application.dto.chatDto import ChatInputDTO, ChatOutputDTO
from src.application.applicationModuleDependency import get_chat_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/message", response_model=Result[ChatOutputDTO])
async def message(dto: ChatInputDTO,
    service: IChatService = Depends(get_chat_service)
):
    result = await service.message(dto)
    
    if not result.success:
        raise ValueError(result.message)
    
    return result 