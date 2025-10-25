"""
SOUP Package Builder - Run this on a CONNECTED machine
Creates encrypted, signed update packages for offline deployment
"""

import os
import json
import hashlib
import zipfile
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

class SOUPBuilder:
    def __init__(self, private_key_path: str, encryption_key: bytes = None):
        # Load private key for signing
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        
        # Generate or use encryption key
        self.cipher = Fernet(encryption_key or Fernet.generate_key())
    
    def create_package(
        self,
        version: str,
        models_dir: Path = None,
        rules_dir: Path = None,
        threat_intel_dir: Path = None,
        output_dir: Path = Path(".")
    ):
        """Create a SOUP update package"""
        print(f"🔨 Building SOUP package v{version}...")
        
        # Create temporary directory
        temp_dir = Path(f"temp_soup_{version}")
        temp_dir.mkdir(exist_ok=True)
        
        manifest = {
            "version": version,
            "created_at": datetime.now().isoformat(),
            "files": []
        }
        
        # Copy files and generate checksums
        if models_dir and models_dir.exists():
            (temp_dir / "models").mkdir(exist_ok=True)
            for file in models_dir.glob("*.pkl") + models_dir.glob("*.tflite"):
                dest = temp_dir / "models" / file.name
                dest.write_bytes(file.read_bytes())
                manifest["files"].append({
                    "path": f"models/{file.name}",
                    "sha512": self._sha512(dest)
                })
        
        if rules_dir and rules_dir.exists():
            (temp_dir / "rules").mkdir(exist_ok=True)
            for file in rules_dir.glob("*.json"):
                dest = temp_dir / "rules" / file.name
                dest.write_bytes(file.read_bytes())
                manifest["files"].append({
                    "path": f"rules/{file.name}",
                    "sha512": self._sha512(dest)
                })
        
        if threat_intel_dir and threat_intel_dir.exists():
            (temp_dir / "threat_intel").mkdir(exist_ok=True)
            for file in threat_intel_dir.glob("*.json"):
                dest = temp_dir / "threat_intel" / file.name
                dest.write_bytes(file.read_bytes())
                manifest["files"].append({
                    "path": f"threat_intel/{file.name}",
                    "sha512": self._sha512(dest)
                })
        
        # Write manifest
        manifest_path = temp_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Create ZIP
        zip_path = temp_dir / "update.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in temp_dir.rglob("*"):
                if file.is_file() and file != zip_path:
                    zipf.write(file, file.relative_to(temp_dir))
        
        # Sign the ZIP
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        signature = self.private_key.sign(
            zip_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Save signature
        sig_path = temp_dir / "signature.sig"
        sig_path.write_bytes(signature)
        
        # Encrypt everything
        encrypted_data = self.cipher.encrypt(zip_data)
        
        # Create final .soup file
        soup_path = output_dir / f"quorum-update-{version}.soup"
        soup_path.write_bytes(encrypted_data)
        
        # Copy signature separately for verification
        (output_dir / f"quorum-update-{version}.sig").write_bytes(signature)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"✅ SOUP package created: {soup_path}")
        print(f"📦 Size: {soup_path.stat().st_size / 1024:.2f} KB")
        print(f"🔐 Signature: {output_dir / f'quorum-update-{version}.sig'}")
        
        return soup_path
    
    def _sha512(self, file_path: Path) -> str:
        """Calculate SHA-512 hash"""
        sha512 = hashlib.sha512()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha512.update(chunk)
        return sha512.hexdigest()


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python soup_builder.py <version>")
        print("Example: python soup_builder.py 2.1.0")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Load encryption key from environment
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        print("❌ ENCRYPTION_KEY not set in environment")
        sys.exit(1)
    
    builder = SOUPBuilder(
        private_key_path="backend/routes/quorum_private.pem",
        encryption_key=encryption_key.encode()
    )
    
    builder.create_package(
        version=version,
        models_dir=Path("backend/data/models"),
        rules_dir=Path("backend/data/rules"),
        threat_intel_dir=Path("backend/data/threat_intel"),
        output_dir=Path(".")
    )
