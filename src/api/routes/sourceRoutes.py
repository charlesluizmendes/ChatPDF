from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi_versionizer.versionizer import api_version

from src.domain.common.result import Result
from src.application.interfaces.sourceService import ISourceService
from src.application.dto.addFileDto import AddFileInputDTO, AddFileOutputDTO
from src.application.dto.deleteFileDto import DeleteFileInputDTO
from src.application.applicationModuleDependency import get_source_service

router = APIRouter(prefix="/source", tags=["Source"])


@api_version(1)
@router.post("/add-file", response_model=Result[AddFileOutputDTO])
async def add_file(file: UploadFile = File(...),
    service: ISourceService = Depends(get_source_service)
):
    dto = AddFileInputDTO(file=file)
    result = await service.add_file(dto)

    if not result.success:
        raise ValueError(result.message)
    
    return result


@api_version(1)
@router.delete("/delete", response_model=Result)
async def delete_file(dto: DeleteFileInputDTO,
    service: ISourceService = Depends(get_source_service)
):
    result = await service.delete_file(dto)

    if not result.success:
        raise ValueError(result.message)
    
    return result