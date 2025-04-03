from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")

class MongoDBConnection:
    def __init__(self, db_uri=None, db_name='crypto_manager'):
        self.client = MongoClient(config["MONGO_URI"])
        self.db = self.client[config["DB_NAME"]]

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def list_collections(self):
        return self.db.list_collection_names()
    
    def create_collection(self, collection_name):
        if collection_name not in self.list_collections():
            self.db.create_collection(collection_name)
            print(f"Colectia '{collection_name}' a fost creata...")
        else:
            print(f"Colectia '{collection_name}' exista deja...")
    
    def close_connection(self):
        self.client.close()
    
    def get_db(self):
        return self.db
    