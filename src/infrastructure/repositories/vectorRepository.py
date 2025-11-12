import io
import fitz
import base64
import pytesseract
from typing import Tuple, Any
from PIL import Image

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

from src.domain.interfaces.repositories.vectorRepository import IVectorRepository
from src.infrastructure.context.mongoContext import MongoContext


class VectorRepository(IVectorRepository):
    def __init__(
        self, 
        context: MongoContext, 
        collection_name: str, 
        index_name: str,
        chunk_size: int,
        chunk_overlap: int,
        tesseract_cmd: str,
        api_key: str
    ):
        self.context = context
        self.collection_name = collection_name
        self.index_name = index_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.api_key = api_key

        self.collection = context.get_collection(self.collection_name)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        self.tesseract_cmd = tesseract_cmd

        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key
        )

    def _extract_with_ocr(self, file_path: str) -> list:
        pdf_document = fitz.open(file_path)
        documents = []

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text().strip()

            if text and len(text) > 50:
                documents.append(Document(
                    page_content=text,
                    metadata={"page": page_num + 1, "source": file_path, "method": "native"}
                ))
            else:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes()))

                custom_config = f'--tessdata-dir "{self.tesseract_cmd}" --oem 3 --psm 6'

                ocr_text = pytesseract.image_to_string(
                    img, 
                    lang='por',
                    config=custom_config
                ).strip()

                if ocr_text and len(ocr_text) > 20:
                    documents.append(Document(
                        page_content=ocr_text,
                        metadata={"page": page_num + 1, "source": file_path, "method": "ocr"}
                    ))

        pdf_document.close()
        return documents

    async def add_vectors(self, source_id: str, file_path: str) -> Tuple[bool, int]:       
        try:
            pages = self._extract_with_ocr(file_path)
            
            documents = self.text_splitter.split_documents(pages)
            chunks_count = len(documents)
            
            for doc in documents:
                doc.metadata["source_id"] = source_id
            
            MongoDBAtlasVectorSearch.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection=self.collection,
                index_name=self.index_name
            )
            
            return True, chunks_count
        
        except Exception:
            raise
    
    async def delete_vectors(self, source_id: str) -> bool:
        try:
            self.collection.delete_many({"source_id": source_id})
            
            return True
        
        except Exception:
            raise
    
    async def get_retriever(self, source_id: str) -> Any:
        try:
            vectordb = MongoDBAtlasVectorSearch(
                collection=self.collection,
                embedding=self.embeddings,
                index_name=self.index_name
            )
        
            retriever = vectordb.as_retriever(
                search_type='similarity',
                search_kwargs={
                    "k": 5,
                    "fetch_k": 30,
                    'pre_filter': {'source_id': str(source_id)}
                }
            )

            return retriever
        
        except Exception:
            raise        