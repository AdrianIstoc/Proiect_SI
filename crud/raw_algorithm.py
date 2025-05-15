import datetime
from mongo import *

class CRUDAlgorithm:
    def __init__(self, connection):
        self.collection = connection.get_collection(config["ALGS_COLLECTION"])

    def get_collection(self):
        return self.collection

    def create_algorithm(self, name, type, key_length_bits, block_size=None, mode=None):
        alg_data={
            "name": name,
            "type": type,
            "key_length_bits": key_length_bits,
            "block_size": block_size,
            "mode": mode,
            "created_at": datetime.datetime.now()
        }
        reslut = self.get_collection().insert_one(alg_data)
        return reslut.inserted_id
    
    def get_all_algorithms(self):
        return list(self.get_collection().find())
    
    def get_algorithm_by_id(self, alg_id):
        return self.get_collection().find({"_id": alg_id})
    
    def get_algorithms_by_type(self, type):
        return list(self.get_collection().find({"type": type}))
    
    def update_algorithm(self, alg_id, name=None, type=None, key_length_bits=None, block_size=None, mode=None):
        update_data = {}
        if name:
            update_data["name"]=name
        if type:
            update_data["type"]=type
        if key_length_bits:
            update_data["key_length_bits"]=key_length_bits
        if block_size:
            update_data["block_size"]=block_size
        if mode:
            update_data["mode"]=mode

        if update_data:
            result = self.get_collection().update_one({"_id": alg_id}, {"$set": update_data})
            return result.modified_count
        
        return 0
    

    def delete_algorithm(self, alg_id):
        result = self.get_collection().delete_one({"_id": alg_id})
        return result.deleted_count