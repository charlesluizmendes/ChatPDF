from abc import ABC, abstractmethod

from src.domain.common.result import Result
from src.application.dto.addFileDto import AddFileInputDTO, AddFileOutputDTO
from src.application.dto.deleteFileDto import DeleteFileInputDTO


class ISourceService(ABC):
    @abstractmethod
    async def add_file(self, dto: AddFileInputDTO) -> Result[AddFileOutputDTO]:
        pass

    @abstractmethod
    async def delete_file(self, dto: DeleteFileInputDTO) -> Result:
        pass
