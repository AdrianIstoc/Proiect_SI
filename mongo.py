from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["crypto_manager"]

files_collection = db["files"]
keys_collection = db["keys"]
performance_collection = db["performance"]

print("Conexiune realizată cu succes la MongoDB Atlas!")
