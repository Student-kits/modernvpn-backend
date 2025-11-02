import secrets
import os

def random_token(n=32):
    return secrets.token_hex(n)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)