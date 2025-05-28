import subprocess
import os
import hashlib
import uuid
from datetime import datetime


#################################################
def calculate_hash(file_path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def generate_uuid():
    return str(uuid.uuid4())


def get_file_metadata(file_path):
    stats = os.stat(file_path)
    return {
        "size": stats.st_size,
        "created": datetime.fromtimestamp(stats.st_ctime),
        "modified": datetime.fromtimestamp(stats.st_mtime)
    }
def generate_random_key(length=32):
    return os.urandom(length)

def key_form_passphrase(passphrase, salt = None, length = 32, iterations=100000):
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations, dklen=length)
    return key, salt

################################################

def encrypt_symmetric(input_file, password, output_file=None, algorithm=None):
    if output_file == None:
        output_file = input_file + ".enc"
    if algorithm == None:
        algorithm="aes-256-cbc"
    cmd = [
        "openssl", "enc", f"-{algorithm}", "-salt", "-pbkdf2",
        "-in", input_file,
        "-out", output_file,
        "-pass", f"pass:{password}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la criptare: {result.stderr}")
    return output_file


def decrypt_symmetric(input_file, password, output_file=None, algorithm=None):
    if output_file == None:
        output_file = input_file[:-4]
    if algorithm == None:
        algorithm="aes-256-cbc"
    cmd = [
        "openssl", "enc", f"-d", f"-{algorithm}", "-pbkdf2",
        "-in", input_file,
        "-out", output_file,
        "-pass", f"pass:{password}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la decriptare: {result.stderr}")
    return output_file


################################################

def generate_rsa_keypair(private_key_file="private.pem", public_key_file="public.pem", key_size=2048):
    subprocess.run([
        "openssl", "genpkey",
        "-algorithm", "RSA",
        "-out", private_key_file,
        "-pkeyopt", f"rsa_keygen_bits:{key_size}"
    ], check = True)

    subprocess.run([
        "openssl", "rsa",
        "-in", private_key_file,
        "-pubout",
        "-out", public_key_file
    ], check= True)

    return private_key_file, public_key_file

def encrypt_asymmetric(input_file, public_key_file, output_file=None):
    if output_file == None:
        output_file = input_file + ".enc"
    
    cmd = [
        "openssl", "pkeyutl",
        "-encrypt",
        "-in", input_file,
        "-pubin",
        "-inkey", public_key_file,
        "-out", output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la criptare asimetrică: {result.stderr}")
    return output_file

def decrypt_asymmetric(input_file, private_key_file, output_file = None):
    if output_file == None:
        output_file = input_file[:-4]
    cmd = [
        "openssl", "pkeyutl",
        "-decrypt",
        "-in", input_file,
        "-inkey", private_key_file,
        "-out", output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la decriptare asimetrică: {result.stderr}")
    return output_file

def encrypt_hybrid(input_file, public_key_file, encrypted_file=None, encrypted_key_file="key.enc"):
    if encrypted_file is None:
        encrypted_file = input_file + ".enc"

    aes_key = generate_random_key(32)

    encrypt_symmetric(input_file, aes_key.hex(), output_file=encrypted_file, algorithm="aes-256-cbc")

    temp_key_file = "temp_aes.key"
    with open(temp_key_file, "wb") as f:
        f.write(aes_key)

    encrypt_asymmetric(temp_key_file, public_key_file, output_file=encrypted_key_file)
    os.remove(temp_key_file)

    return encrypted_file, encrypted_key_file


def decrypt_hybrid(encrypted_file, encrypted_key_file, private_key_file, output_file=None):
    if output_file is None:
        output_file = encrypted_file.replace(".enc", "_decrypted.txt")

    temp_key_file = "temp_dec_aes.key"
    decrypt_asymmetric(encrypted_key_file, private_key_file, output_file=temp_key_file)

    with open(temp_key_file, "rb") as f:
        aes_key = f.read()
    os.remove(temp_key_file)

    decrypt_symmetric(encrypted_file, aes_key.hex(), output_file=output_file, algorithm="aes-256-cbc")
    return output_file
