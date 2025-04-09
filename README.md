# Proiect_SI
un proiect foarte bun de altfel







""" Exemplu de utilizare a conexiunii cu baza de date """

from mongo import *
from crud.crud_files import *
from crud.crud_keys import *
from crud.crut_performances import *
from pprint import pprint


connection = MongoDBConnection()

files_collection = CRUDFiles(connection)

file_id = files_collection.create_file("document.txt", 1000, "document.enc", "AES-256", key_id="some_key_id")
print(f"Fisier creat cu ID: {file_id}")

files = files_collection.get_all_files()
pprint(files)

modified_count = files_collection.update_file_status(file_id, "decrypted")
print(f"Fisierul a fost modificat: {modified_count} fisiere")

deleted_count = files_collection.delete_file(file_id)
print(f"Fisier sters: {deleted_count} fisiere")


keys_collection = CRUDKeys(connection)

key_id = keys_collection.create_key(algorithm="AES-256", key="base64_key_value", key_type="symmetric", expires_at=datetime.datetime(2025, 4, 4))
print(f"Cheie creata cu ID: {key_id}")

keys = keys_collection.get_all_keys()
pprint(keys)

modified_count = keys_collection.update_key(key_id, key="new_base64_key")
print(f"Cheia a fost modificata: {modified_count} chei")

deleted_count = keys_collection.delete_key(key_id)
print(f"Cheie stearsa: {deleted_count} chei")



perfs_collection = CRUDPerformances(connection)

perf_id = perfs_collection.create_performance("fileID", "AES-256", "encryption", 0.47, 1980, 10000)
print(f"Performanta creata cu ID: {perf_id}")

perfs = perfs_collection.get_all_performances()
pprint(perfs)

modified_count = perfs_collection.update_performance(perf_id, 0.33, 10000)
print(f"Performanta a fost modificata: {modified_count} performante")

deleted_count = perfs_collection.delete_performance(perf_id)
print(f"Performanta stearsa: {deleted_count} performante")


connection.close_connection()