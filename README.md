# Proiect_SI
un proiect foarte bun de altfel







""" Exemplu de utilizare a conexiunii cu baza de date """

from mongo import *
from crud.crud_files import *
from crud.crud_keys import *
from crud.crut_performances import *
from crud.raw_algorithm import *
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

key_id = keys_collection.create_key(algorithm_id="test", key="base64_key_value", key_type="symmetric", expires_at=datetime.datetime(2025, 4, 4))
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


algs_collection = CRUDAlgorithm(connection)

alg_id = algs_collection.create_algorithm("help", "licenta", "goes", "very", "bad")
print(f"Algoritm creat cu ID: {alg_id}")

algs = algs_collection.get_all_algorithms()
pprint(algs)

modified_count = algs_collection.update_algorithm(alg_id, name="HEEEEEEEEEEELP VREAU SA PLANG")
print(f"Algoritmul a fost modificat: {modified_count} algoritmi")

deleted_count = algs_collection.delete_algorithm(alg_id)
print(f"Algoritm sters: {deleted_count} algoritmi")



connection.close_connection()




""" Exemplu de utilizare a openssl (no utilz included) """

import subprocess
import os

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
input_file = os.path.join(desktop_path, "chestie dppd.txt")
output_file = os.path.join(desktop_path, "chestie dppd.txt.enc")

parola = "abcdefgh"

cmd = [
    "openssl", "enc", "-aes-256-cbc", "-salt",
    "-in", input_file,
    "-out", output_file,
    "-pass", f"pass:{parola}"
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode==0:
    print("Fisier criptat cu succes!")
else:
    print("Eroare la criptare:")
    print(result.stderr)







""" Exemplu de utilizare a openssl (utilz included) """


import time
import os
import psutil
from crud.crud_files import *
from crud.crud_keys import *
from crud.crut_performances import *
from crud.raw_algorithm import *
from utilz.openssl_utils import *
from mongo import *
from pprint import pprint

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
input_file = os.path.join(desktop_path, "chestie dppd.txt")
output_file = os.path.join(desktop_path, "chestie dppd.txt.enc")

parola = "abcdefgh"

algorithm_name = "AES"
algorithm_type = "symmetric"
key_length_bits=256
block_size = 128
mode = "CBC"


connection = MongoDBConnection()

alg_conn = CRUDAlgorithm(connection)
key_conn = CRUDKeys(connection)
fle_conn = CRUDFiles(connection)
prf_conn = CRUDPerformances(connection)

alg_id = alg_conn.create_algorithm(algorithm_name, algorithm_type, key_length_bits, block_size, mode)
key_id = key_conn.create_key(alg_id, parola)

start_time = time.perf_counter()
process = psutil.Process(os.getpid())
mem_before = process.memory_info().rss

encrypt_file(input_file, output_file, parola, algorithm="aes-256-cbc")

end_time = time.perf_counter()
mem_after = process.memory_info().rss

execution_time = end_time - start_time
memory_used = mem_after - mem_before

meta = get_file_metadata(input_file)

fle_id = fle_conn.create_file(os.path.basename(input_file), meta["size"], os.path.basename(output_file), alg_id, key_id, )

prf_id = prf_conn.create_performance(fle_id, alg_id, "encrypt", execution_time, memory_used, meta["size"])


pprint(fle_conn.get_all_files())
pprint(key_conn.get_all_keys())
pprint(prf_conn.get_all_performances())
pprint(alg_conn.get_all_algorithms())