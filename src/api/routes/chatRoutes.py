from fastapi import APIRouter, Depends
from fastapi_versionizer.versionizer import api_version

from src.domain.common.result import Result
from src.application.interfaces.chatService import IChatService
from src.application.dto.chatDto import ChatInputDTO, ChatOutputDTO
from src.application.applicationModuleDependency import get_chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@api_version(1)
@router.post("/message", response_model=Result[ChatOutputDTO])
async def message(dto: ChatInputDTO,
    service: IChatService = Depends(get_chat_service)
):
    result = await service.message(dto)
    
    if not result.success:
        raise ValueError(result.message)
    
    return result