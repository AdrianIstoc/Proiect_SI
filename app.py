from mongo import *
from dotenv import dotenv_values

connection = MongoDBConnection()

collection = connection.get_collection(config["TEST"])

# collection.insert_one({"_id": 2, "message": "A doua inserare"})






# documents = collection.find()
# for doc in documents:
#     print(doc)



connection.create_collection(config["FILE_COLLECTION"])

print("Colectiile din DB: ", connection.list_collections())

connection.close_connection()

# print("Hello!")

# config = dotenv_values(".env")


# client = MongoClient(config["MONGO_URI"])

# db = client[config["DB_NAME"]]
# collection = db["files"]

# print("Bye!")
# print(db.list_collection_names())