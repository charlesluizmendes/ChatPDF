from typing import Optional
from datetime import datetime


class PdfModel:   
    @staticmethod
    def to_dict(source_id: str, filename: str, chunks_count: int, 
                created_at: datetime, metadata: Optional[dict] = None) -> dict:
        return {
            "source_id": source_id,
            "filename": filename,
            "chunks_count": chunks_count,
            "created_at": created_at,
            "metadata": metadata
        }
    
    @staticmethod
    def from_dict(data: dict) -> dict:
        return {
            "source_id": data.get("source_id"),
            "filename": data.get("filename"),
            "chunks_count": data.get("chunks_count"),
            "created_at": data.get("created_at"),
            "metadata": data.get("metadata")
        }