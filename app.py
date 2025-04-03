from mongo import *
from crud.crud_files import *

connection = MongoDBConnection()

files_collection = CRUDFiles(connection)

file_id = files_collection.create_document("document.txt", "document.enc", "AES-256", key_id="some_key_id")
print(f"Fișier creat cu ID: {file_id}")

files = files_collection.get_all_documents()
print(files)

modified_count = files_collection.update_file_status(file_id, "decrypted")
print(f"Fișierul a fost modificat: {modified_count} documente")

deleted_count = files_collection.delete_file(file_id)
print(f"Fișier șters: {deleted_count} documente")

connection.close_connection()