import datetime
from mongo import *

class CRUDKeys:
    def __init__(self, connection):
        self.collection = connection.get_collection(config["KEYS_COLLECTION"])

    def get_collection(self):
        return self.collection
    
    def create_key(self, algorithm_id, key, key_type="symmetric", expires_at=None, public_key=None, private_key=None):
        key_data={
            "algorithm_id": algorithm_id,
            "key": key,
            "key_type": key_type,
            "created_at": datetime.datetime.utcnow(),
            "expires_at": expires_at,
            "public_key": public_key if key_type == "asymmetric" else None,
            "private_key": private_key if key_type == "asymmetric" else None
        }
        result = self.get_collection().insert_one(key_data)
        return result.inserted_id
    
    def get_all_keys(self):
        return list(self.get_collection().find())
    
    def get_key_by_id(self, key_id):
        return self.get_collection().find_one({"_id": key_id})
    
    def get_keys_by_type(self, key_type):
        return list(self.get_collection().find({"key_type": key_type}))
    
    def update_key(self, key_id, algorithm_id=None, key=None, expires_at=None, public_key=None, private_key=None):
        update_data = {}
        if algorithm_id:
            update_data["algorithm_id"]=algorithm_id
        if key:
            update_data["key"] = key
        if expires_at:
            update_data["expires_at"] = expires_at
        if public_key:
            update_data["public_key"] = public_key
        if private_key:
            update_data["private_key"] = private_key

        if update_data:
            result = self.get_collection().update_one({"_id": key_id}, {"$set": update_data})
            return result.modified_count
        
        return 0
    

    def delete_key(self, key_id):
        result = self.get_collection().delete_one({"_id": key_id})
        return result.deleted_count
    
