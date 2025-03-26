from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:test@cluster0.ncqlb.mongodb.net/")

db = client["crypto_manager"]

files_collection = db["files"]
keys_collection = db["keys"]
performance_collection = db["performance"]

print("Conexiune realizată cu succes la MongoDB Atlas!")
