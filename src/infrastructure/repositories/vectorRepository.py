import fitz
import base64
from typing import Tuple, Any

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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
        model: str,
        api_key: str
    ):
        self.context = context
        self.collection_name = collection_name
        self.index_name = index_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = model
        self.api_key = api_key

        self.collection = context.get_collection(self.collection_name)
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0.0
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key
        )

    def _extract_with_vision(self, file_path: str) -> list:
        pdf_document = fitz.open(file_path)
        documents = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            pixels = page.get_pixmap(dpi=200)
            img_bytes = pixels.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')

            response = self.llm.invoke([
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": "Extraia e descreva TODO o conteúdo desta página."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                        }
                    ]
                )
            ])

            text = response.content
                        
            if text and text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={"page": page_num + 1, "source": file_path}
                ))
        
        pdf_document.close()
        return documents


    async def add_vectors(self, source_id: str, file_path: str) -> Tuple[bool, int]:       
        try:
            pages = self._extract_with_vision(file_path)
            
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