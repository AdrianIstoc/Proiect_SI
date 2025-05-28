# Proiect_SI
un proiect foarte bun de altfel


###CRIPTARE SIMETRICA###
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

connection = MongoDBConnection()

alg_conn = CRUDAlgorithm(connection)
key_conn = CRUDKeys(connection)
fle_conn = CRUDFiles(connection)
prf_conn = CRUDPerformances(connection)


#simetric
algorithm_name = "AES"
algorithm_type = "symmetric"
key_length_bits = 256
block_size = 128
mode = "CBC"

parola = generate_random_key()

alg_id = alg_conn.create_algorithm(algorithm_name, algorithm_type, key_length_bits, block_size, mode)
key_id = key_conn.create_key(alg_id, parola.hex())

process = psutil.Process(os.getpid())
start_time = time.perf_counter()
mem_before = process.memory_info().rss

encrypted_file = encrypt_symmetric(input_file, parola.hex())

end_time = time.perf_counter()
mem_after = process.memory_info().rss
execution_time = end_time - start_time
memory_used = mem_after - mem_before

hash_original = calculate_hash(input_file)
meta = get_file_metadata(input_file)
fle_id = fle_conn.create_file(os.path.basename(input_file), meta["size"], encrypted_file, alg_id, key_id, file_hash=hash_original)
prf_id = prf_conn.create_performance(fle_id, alg_id, "encrypt", execution_time, memory_used, meta["size"])



decrypted_file = input_file.replace(".txt", "_decrypted.txt")
start_time = time.perf_counter()
mem_before = process.memory_info().rss

decrypt_symmetric(encrypted_file, parola.hex(), decrypted_file)

end_time = time.perf_counter()
mem_after = process.memory_info().rss

execution_time = end_time - start_time
mem_after = mem_after - mem_before

hash_decrypted = calculate_hash(decrypted_file)
meta_dec = get_file_metadata(decrypted_file)
fle_dec_id = fle_conn.create_file(os.path.basename(decrypted_file), meta_dec["size"], decrypted_file, alg_id, key_id, status="decrypted", file_hash=hash_decrypted)
prf_dec_id = prf_conn.create_performance(fle_dec_id, alg_id, "decrypt", execution_time, memory_used, meta_dec["size"])

if hash_original == hash_decrypted:
    print("Fisierul decriptat este identic cu originalul")
else:
    print("Fisierul decriptat este diferit de original")

f = fle_conn.get_all_files()
k = key_conn.get_all_keys()
p = prf_conn.get_all_performances()
a = alg_conn.get_all_algorithms()

pprint(f)
pprint(k)
pprint(p)
pprint(a)

for i in f:
    if fle_conn.delete_file(i['_id']) == 1:
        print(f"File {i['_id']} deleted")
for i in k:
    if key_conn.delete_key(i['_id']) == 1:
        print(f"Key {i['_id']} deleted")
for i in p:
    if prf_conn.delete_performance(i['_id']) == 1:
        print(f"Perormance {i['_id']} deleted")
for i in a:
    if alg_conn.delete_algorithm(i['_id']) == 1:
        print(f"Algorithm {i['_id']} deleted")



###CRIPTARE ASIMETRICA(HIBIRDA)###
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
private_key_file = os.path.join(desktop_path, "private.pem")
public_key_file = os.path.join(desktop_path, "public.pem")


connection = MongoDBConnection()

alg_conn = CRUDAlgorithm(connection)
key_conn = CRUDKeys(connection)
fle_conn = CRUDFiles(connection)
prf_conn = CRUDPerformances(connection)


#asimetric
algorithm_name = "RSA"
algorithm_type = "asymmetric"
key_length_bits = 2048

generate_rsa_keypair(private_key_file, public_key_file)

with open(private_key_file, 'r') as f:
    private_key_content = f.read()
with open(public_key_file, 'r') as f:
    public_key_content = f.read()



alg_id = alg_conn.create_algorithm(algorithm_name, algorithm_type, key_length_bits)
key_id = key_conn.create_key(alg_id, key_type="asymmetric", public_key=public_key_content, private_key=private_key_content)

process = psutil.Process(os.getpid())
start_time = time.perf_counter()
mem_before = process.memory_info().rss

encrypted_file, ecrypted_key_file = encrypt_hybrid(input_file, public_key_file)
end_time = time.perf_counter()
mem_after = process.memory_info().rss
execution_time = end_time - start_time
memory_used = mem_after - mem_before

hash_original = calculate_hash(input_file)
meta = get_file_metadata(input_file)
fle_id = fle_conn.create_file(os.path.basename(input_file), meta["size"], encrypted_file, alg_id, key_id, file_hash=hash_original)
prf_id = prf_conn.create_performance(fle_id, alg_id, "encrypt", execution_time, memory_used, meta["size"])



decrypted_file = input_file.replace(".txt", "_decrypted.txt")
start_time = time.perf_counter()
mem_before = process.memory_info().rss

decrypt_hybrid(encrypted_file, ecrypted_key_file, private_key_file, decrypted_file)

end_time = time.perf_counter()
mem_after = process.memory_info().rss

execution_time = end_time - start_time
mem_after = mem_after - mem_before

hash_decrypted = calculate_hash(decrypted_file)
meta_dec = get_file_metadata(decrypted_file)
fle_dec_id = fle_conn.create_file(os.path.basename(decrypted_file), meta_dec["size"], decrypted_file, alg_id, key_id, status="decrypted", file_hash=hash_decrypted)
prf_dec_id = prf_conn.create_performance(fle_dec_id, alg_id, "decrypt", execution_time, memory_used, meta_dec["size"])

if hash_original == hash_decrypted:
    print("Fisierul decriptat este identic cu originalul")
else:
    print("Fisierul decriptat este diferit de original")

f = fle_conn.get_all_files()
k = key_conn.get_all_keys()
p = prf_conn.get_all_performances()
a = alg_conn.get_all_algorithms()

pprint(f)
pprint(k)
pprint(p)
pprint(a)

for i in f:
    if fle_conn.delete_file(i['_id']) == 1:
        print(f"File {i['_id']} deleted")
for i in k:
    if key_conn.delete_key(i['_id']) == 1:
        print(f"Key {i['_id']} deleted")
for i in p:
    if prf_conn.delete_performance(i['_id']) == 1:
        print(f"Perormance {i['_id']} deleted")
for i in a:
    if alg_conn.delete_algorithm(i['_id']) == 1:
        print(f"Algorithm {i['_id']} deleted")


