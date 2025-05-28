import datetime
from mongo import *

class CRUDFiles:
    def __init__(self, connection):
        self.collection = connection.get_collection(config["FILE_COLLECTION"])

    def get_collection(self):
        return self.collection
    
    def create_file(self, filename, file_size_bytes, encrypted_filename, algorithm_id, key_id, status="encrypted", file_hash = None):
        now = datetime.datetime.now()
        file_data = {
            "filename": filename,
            "file_size_bytes": file_size_bytes,
            "encrypted_filename": encrypted_filename,
            "algorithm_id": algorithm_id,
            "key_id": key_id,
            "status": status,
            "file_hash": file_hash,
            "created_at": now
        }
        result = self.get_collection().insert_one(file_data)
        return result.inserted_id
    
    def get_all_files(self):
        return list(self.get_collection().find())
    
    def get_file_by_id(self, file_id):
        return self.get_collection().find_one({"_id": file_id})
    
    def get_files_by_algorithm(self, algorithm_id):
        return list(self.get_collection().find({"algorithm_id": algorithm_id}))
    
    def update_file_status(self, file_id, status):
        update_data={
            "status": status,
            "updated_at": datetime.datetime.now()
        }
        result = self.get_collection().update_one({"_id": file_id}, {"$set": update_data})
        return result.modified_count
    
    def update_file(self, file_id, encrypted_filename=None, algorithm_id=None):
        update_data={}
        if encrypted_filename:
            update_data["encrypted_filename"]=encrypted_filename
        if algorithm_id:
            update_data["algorithm_id"] = algorithm_id
        
        if update_data:
            update_data["updated_at"]=datetime.datetime.now()
            result = self.get_collection().update_one({"_id": file_id}, {"$set": update_data})
            return result.modified_count
        
        return 0
    
    def delete_file(self, file_id):
        result = self.get_collection().delete_one({"_id": file_id})
        return result.deleted_count