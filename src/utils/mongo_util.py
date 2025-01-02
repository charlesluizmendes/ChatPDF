import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_url = os.getenv("MONGO_URL")
mongo_db = os.getenv("MONGO_DB")
mongo_collection = os.getenv("MONGO_COLLECTION")

class MongoDBConnectionManager:
    def __init__(self):
        self.mongo_url = mongo_url
        self.client = None

    def connect(self):
        if not self.client:
            self.client = MongoClient(self.mongo_url, ssl=True, tls=True)
        return self.client

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

class MongoDBDocumentHandler:
    def __init__(self, embeddings, connection_manager: MongoDBConnectionManager):
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.embeddings = embeddings
        self.connection_manager = connection_manager

    def similarity_search(self, query="", k=10, pre_filter=None):
        client = self.connection_manager.connect()
        collection = client[self.mongo_db][self.mongo_collection]

        from langchain_mongodb import MongoDBAtlasVectorSearch

        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embeddings,
            index_name="vector_index",
            relevance_score_fn="cosine"
        )

        results = vector_store.similarity_search(
            query=query, 
            k=k, 
            pre_filter=pre_filter
        )

        return results

    def get_retriever(self, search_type="mmr", search_kwargs=None):
        if search_kwargs is None:
            search_kwargs = {}

        client = self.connection_manager.connect()
        collection = client[self.mongo_db][self.mongo_collection]

        from langchain_mongodb import MongoDBAtlasVectorSearch

        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embeddings,
            index_name="vector_index",
            relevance_score_fn="cosine"
        )

        retriever = vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

        return retriever

    def add_documents(self, docs):
        client = self.connection_manager.connect()
        collection = client[self.mongo_db][self.mongo_collection]

        from langchain_mongodb import MongoDBAtlasVectorSearch

        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embeddings,
            index_name="vector_index",
            relevance_score_fn="cosine"
        )
        
        vector_store.add_documents(docs)

    def delete_documents(self, ids=[]):
        client = self.connection_manager.connect()
        collection = client[self.mongo_db][self.mongo_collection]

        from langchain_mongodb import MongoDBAtlasVectorSearch

        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embeddings,
            index_name="vector_index",
            relevance_score_fn="cosine"
        )

        result = vector_store.delete(
            ids=ids
        )
        
        return result