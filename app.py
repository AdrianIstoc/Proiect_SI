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