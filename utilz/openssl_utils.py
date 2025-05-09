import subprocess
import os
import hashlib
import uuid
from datetime import datetime

#generate symetric key
def generate_openssl_key(passphrase: str, key_file_path: str):
    cmd = [
        "openssl", "enc", "-aes-256-cbc", "-k", passphrase, "-P", "-md", "sha256"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout
    else:
        raise RuntimeError(f"Eroare la generare cheie: {result.stderr}")



def encrypt_file(input_file, output_file, password, algorithm="aes-256-cbc"):
    cmd = [
        "openssl", "enc", f"-{algorithm}", "-salt",
        "-in", input_file,
        "-out", output_file,
        "-pass", f"pass:{password}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la criptare: {result.stderr}")
    return True


def decrypt_file(input_file, output_file, password, algorithm="aes-256-cbc"):
    cmd = [
        "openssl", "enc", f"-d", f"-{algorithm}",
        "-in", input_file,
        "-out", output_file,
        "-pass", f"pass:{password}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Eroare la decriptare: {result.stderr}")
    return True


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
