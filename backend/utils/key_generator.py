#!/usr/bin/env python3
import secrets
from cryptography.fernet import Fernet
from pathlib import Path

def generate_keys():
    fernet_key = Fernet.generate_key().decode()  # base64 urlsafe, 32 bytes underlying
    soup_key = secrets.token_urlsafe(32)          # >=32 chars, urlsafe
    jwt_secret = secrets.token_hex(32)            # 64 hex chars, 32 bytes

    return {
        "ENCRYPTION_KEY": fernet_key,
        "SOUP_SIGNING_KEY": soup_key,
        "JWT_SECRET_KEY": jwt_secret
    }

def write_env(out_path: str = "keys.env"):
    keys = generate_keys()
    p = Path(out_path)
    with p.open("w") as f:
        for k, v in keys.items():
            f.write(f"{k}={v}\n")
    print(f"Wrote keys to {p.resolve()}")
    for k, v in keys.items():
        print(f"{k}={v}")

if __name__ == "__main__":
    write_env()
