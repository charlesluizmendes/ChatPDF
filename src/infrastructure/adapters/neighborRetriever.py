from typing import List, Any
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
from pydantic import ConfigDict

class NeighborRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _retriever: Any
    _collection: Any
    _source_id: str
    
    def __init__(
        self, 
        retriever: Any, 
        collection: Any, 
        source_id: str
    ):
        super().__init__()
        object.__setattr__(self, '_retriever', retriever)
        object.__setattr__(self, '_collection', collection)
        object.__setattr__(self, '_source_id', source_id)
    
    def _get_relevant_documents(
        self, 
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs = self._retriever.invoke(query)
        
        indices = set()
        for doc in docs:
            idx = doc.metadata.get('chunk_index')
            if idx is not None:
                indices.update([idx - 1, idx, idx + 1])
        
        if not indices:
            return docs
        
        neighbors = self._collection.find({
            'source_id': self._source_id,
            'chunk_index': {'$in': list(indices)}
        }).sort('chunk_index', 1)
        
        seen = set()
        result = []
        for n in neighbors:
            idx = n.get('chunk_index')
            if idx not in seen:
                seen.add(idx)
                result.append(Document(
                    page_content=n.get('text', ''),
                    metadata=n.get('metadata', {})
                ))
        
        return result
    
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self._get_relevant_documents(query, run_manager=run_manager)