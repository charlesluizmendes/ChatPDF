from typing import Tuple, Any

from langchain_community.document_loaders.pdf import PyPDFLoader
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
        api_key: str
    ):
        self.context = context
        self.collection = context.get_collection(collection_name)
        self.index_name = index_name
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.embeddings = OpenAIEmbeddings(
            api_key=api_key
        )
    
    async def add_vectors(self, source_id: str, file_path: str) -> Tuple[bool, int]:       
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
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