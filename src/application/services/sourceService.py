import uuid
import os
import tempfile
from datetime import datetime

from src.domain.common.result import Result
from src.domain.entities.pdf import Pdf
from src.domain.interfaces.repositories.pdfRepository import IPdfRepository
from src.domain.interfaces.repositories.vectorRepository import IVectorRepository
from src.application.interfaces.sourceService import ISourceService
from src.application.dto.addFileDto import AddFileInputDTO, AddFileOutputDTO
from src.application.dto.deleteFileDto import DeleteFileInputDTO


class SourceService(ISourceService):
    def __init__(
        self,
        pdf_repository: IPdfRepository,
        vector_repository: IVectorRepository
    ):
        self.pdf_repository = pdf_repository
        self.vector_repository = vector_repository
    
    async def add_file(self, dto: AddFileInputDTO) -> Result[AddFileOutputDTO]:
        filename = getattr(dto.file, 'filename')
        if not filename.endswith('.pdf'):
            return Result.error("Apenas arquivos PDF são aceitos")
        
        source_id = str(uuid.uuid4())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            metadata = dto.file.file.read()
            tmp_file.write(metadata)
            tmp_path = tmp_file.name
        
        try:
            success, chunks_count = await self.vector_repository.add_vectors(source_id, tmp_path)
            
            if not success:
                return Result.error("Erro ao adicionar vetores ao banco")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        pdf_document = Pdf(
            source_id=source_id,
            filename=filename,
            chunks_count=chunks_count,
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        
        document_added = await self.pdf_repository.add(pdf_document)
        if not document_added:
            await self.vector_repository.delete_vectors(source_id)
            return Result.error("Erro ao salvar metadados do documento")
        
        output = AddFileOutputDTO(source_id=source_id)            
        return Result.ok(data=output)
        
    async def delete_file(self, dto: DeleteFileInputDTO) -> Result:
        exists = await self.pdf_repository.exists(dto.source_id)
        if not exists:
            return Result.error("Documento não encontrado")
        
        vectors_deleted = await self.vector_repository.delete_vectors(dto.source_id)
        if not vectors_deleted:
            return Result.error("Erro ao remover vetores")
        
        document_deleted = await self.pdf_repository.delete(dto.source_id)
        if not document_deleted:
            return Result.error("Erro ao remover metadados")
        
        return Result.ok()