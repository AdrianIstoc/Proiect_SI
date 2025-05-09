import datetime
from mongo import *

class CRUDPerformances:
    def __init__(self, connection):
        self.collection = connection.get_collection(config["PRFS_COLLECTION"])

    def get_collection(self):
        return self.collection
    
    def create_performance(self, file_id, algorithm_id, operation, execution_time_seconds, memory_usage_byte, file_size_bytes):
        perf_data = {
            "file_id": file_id,
            "algorithm_id": algorithm_id,
            "operation": operation,
            "execution_time_seconds": execution_time_seconds,
            "memory_usage_bytes": memory_usage_byte,
            "execution_time_per_byte": execution_time_seconds / file_size_bytes if file_size_bytes else None,
            "created_at": datetime.datetime.utcnow()
        }
        result = self.get_collection().insert_one(perf_data)
        return result.inserted_id
    
    def get_all_performances(self):
        return list(self.get_collection().find())
    
    def get_performances_by_file(self, file_id):
        return list(self.get_collection().find({"file_id": file_id}))
    
    def get_performances_by_algorithm(self, algorithm_id):
        return list(self.get_collection().find({"algorithm_id": algorithm_id}))
    
    def get_performances_by_operation(self, operation):
        return list(self.get_collection().find({"operation": operation}))
    
    def get_top_performances_per_byte(self, limit=5):
        return list(self.get_collection().find().sort("execution_time_per_byte", 1).limit(limit))
    
    def update_performance(self, perf_id, execution_time_seconds=None, file_size_bytes=None, memory_usage_bytes=None):
        update_data = {}

        if (execution_time_seconds is not None and file_size_bytes is None) or (file_size_bytes is not None and execution_time_seconds is None):
            raise ValueError("Timpul de executie si dimensiunea fisierului trebui furnizate impreuna")

        if execution_time_seconds is not None:
            update_data["execution_time_seconds"] = execution_time_seconds
            update_data["execution_time_per_byte"] = execution_time_seconds / file_size_bytes
        if memory_usage_bytes is not None:
            update_data["memory_usage_bytes"] = memory_usage_bytes

        if update_data:
            result = self.get_collection().update_one({"_id": perf_id}, {"$set": update_data})
            return result.modified_count
        return 0
    
    def delete_performance(self, perf_id):
        result = self.get_collection().delete_one({"_id": perf_id})
        return result.deleted_count