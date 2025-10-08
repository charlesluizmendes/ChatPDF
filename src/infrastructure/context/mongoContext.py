from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection


class MongoContext:
    def __init__(
        self, 
        mongo_url: str, 
        database_name: str
    ):
        self.client: MongoClient = MongoClient(mongo_url)
        self.database: Database = self.client[database_name]
    
    def get_collection(self, collection_name: str) -> Collection:
        return self.database[collection_name]
    
    def close(self):
        self.client.close()