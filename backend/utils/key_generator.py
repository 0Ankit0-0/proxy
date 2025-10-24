from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
routes_dir = os.path.abspath(os.path.join(script_dir, '..', 'routes'))

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize private key
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL, # PKCS1 for compatibility with openssl
    encryption_algorithm=serialization.NoEncryption()
)

with open(os.path.join(routes_dir, 'quorum_private.pem'), 'wb') as f:
    f.write(private_pem)

# Generate public key
public_key = private_key.public_key()

# Serialize public key
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open(os.path.join(routes_dir, 'quorum_public.pem'), 'wb') as f:
    f.write(public_pem)

print("Keys generated successfully in backend/routes directory.")
