from typing import Optional
from bson import Binary

from src.domain.interfaces.repositories.pdfRepository import IPdfRepository
from src.domain.entities.pdf import Pdf
from src.infrastructure.context.mongoContext import MongoContext
from src.infrastructure.models.pdfModel import PdfModel


class PdfRepository(IPdfRepository):
    def __init__(self, context: MongoContext, collection_name: str):
        self.context = context
        self.collection = context.get_collection(collection_name)
    
    async def add(self, document: Pdf) -> bool:
        try:
            doc_dict = PdfModel.to_dict(
                source_id=document.source_id,
                filename=document.filename,
                chunks_count=document.chunks_count,
                created_at=document.created_at,
                metadata=Binary(document.metadata)
            )

            self.collection.insert_one(doc_dict)

            return True
        
        except Exception:
            raise
    
    async def delete(self, source_id: str) -> bool:
        try:
            delete = self.collection.delete_one({"source_id": source_id})
            result = delete.deleted_count > 0

            return result
        
        except Exception:
            raise

    async def get_by_id(self, source_id: str) -> Optional[Pdf]:
        try:
            doc = self.collection.find_one({"source_id": source_id})
            if not doc:
                return None
        
            doc_data = PdfModel.from_dict(doc)
            pdf = Pdf(
                source_id=doc_data["source_id"],
                filename=doc_data["filename"],
                chunks_count=doc_data["chunks_count"],
                created_at=doc_data["created_at"],
                metadata=doc_data["metadata"]
            )

            return pdf
        
        except Exception:
            raise       
    
    async def exists(self, source_id: str) -> bool:
        try:
            result = self.collection.count_documents({"source_id": source_id}) > 0

            return result
        
        except Exception:
            raise        