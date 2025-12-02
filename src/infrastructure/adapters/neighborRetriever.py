from typing import List, Any
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
from pydantic import ConfigDict, Field


class NeighborRetriever(BaseRetriever):    
    retriever: Any = Field(default=None, exclude=True)
    collection: Any = Field(default=None, exclude=True)
    source_id: str = Field(default="", exclude=True)
    
    def __init__(
        self, 
        retriever: Any, 
        collection: Any, 
        source_id: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.retriever = retriever
        self.collection = collection
        self.source_id = source_id


    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Document]:
        docs = self.retriever.invoke(query)
        
        indices = set()
        for doc in docs:
            idx = doc.metadata.get('chunk_index')
            if idx is not None:
                indices.update([idx - 1, idx, idx + 1])
        
        if not indices:
            return docs
        
        indices = {i for i in indices if i >= 0}
        
        neighbors = list(self.collection.find({
            'source_id': self.source_id,
            'chunk_index': {'$in': list(indices)}
        }).sort('chunk_index', 1))
        
        seen = set()
        result = []
        
        for n in neighbors:
            idx = n.get('chunk_index')
            if idx is not None and idx not in seen:
                seen.add(idx)
                
                result.append(Document(
                    page_content=n.get('text', ''),
                    metadata={
                        'page': n.get('page'),
                        'source': n.get('source'),
                        'method': n.get('method'),
                        'source_id': n.get('source_id'),
                        'chunk_index': idx
                    }
                ))
        
        return result if result else docs


    async def _aget_relevant_documents(self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun = None) -> List[Document]:
        return self._get_relevant_documents(query, run_manager=run_manager)