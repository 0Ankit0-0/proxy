from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import hashlib
import zipfile
from pathlib import Path

class SOUPHandler:
    """Secure Offline Update Protocol"""

    def __init__(self, encryption_key: bytes = None):
        self.cipher = Fernet(encryption_key or Fernet.generate_key())

    def verify_signature(self, update_file: Path, signature: bytes, public_key) -> bool:
        """Verify digital signature of SOUP package"""
        with open(update_file, 'rb') as f:
            data = f.read()

        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def validate_checksum(self, file_path: Path, expected_hash: str) -> bool:
        """Validate SHA-512 checksum"""
        sha512 = hashlib.sha512()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha512.update(chunk)
        return sha512.hexdigest() == expected_hash

    def extract_update(self, encrypted_package: Path, output_dir: Path) -> dict:
        """Extract and validate SOUP package"""
        # Decrypt
        with open(encrypted_package, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)

        temp_zip = output_dir / "temp_update.zip"
        with open(temp_zip, 'wb') as f:
            f.write(decrypted_data)

        # Extract
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        temp_zip.unlink()  # Clean up

        return {"status": "success", "extracted_to": str(output_dir)}
