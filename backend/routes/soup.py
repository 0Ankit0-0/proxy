from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import json
from datetime import datetime
from core.soup_handlers import SOUPHandler
from config import UPDATES_DIR, MODELS_DIR, SOUP_SIGNING_KEY, ENCRYPTION_KEY
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

router = APIRouter()

# Initialize SOUP handler
soup_handler = SOUPHandler(encryption_key=ENCRYPTION_KEY.encode() if ENCRYPTION_KEY else None)

# Store update history
UPDATE_HISTORY_FILE = UPDATES_DIR / "update_history.json"

def load_update_history():
    """Load update history from file"""
    if UPDATE_HISTORY_FILE.exists():
        with open(UPDATE_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_update_history(update_info: dict):
    """Save update to history"""
    history = load_update_history()
    history.append(update_info)
    with open(UPDATE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@router.post("/update")
async def apply_soup_update(file: UploadFile = File(...)):
    """
    Apply SOUP (Secure Offline Update Protocol) package
    
    Expected package structure:
    - update.soup (encrypted zip containing):
      - manifest.json (metadata, checksums, signatures)
      - models/ (updated AI models)
      - rules/ (updated parsing rules)
      - threat_intel/ (updated threat intelligence)
      - signature.sig (digital signature)
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.soup'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Expected .soup file"
            )
        
        # Save uploaded file
        temp_package = UPDATES_DIR / file.filename
        with open(temp_package, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # Create extraction directory
        extract_dir = UPDATES_DIR / f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Extract encrypted package
        print("📦 Extracting SOUP package...")
        extraction_result = soup_handler.extract_update(temp_package, extract_dir)
        
        # Step 2: Load and verify manifest
        manifest_path = extract_dir / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=400, detail="Invalid SOUP package: manifest.json not found")
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"📋 Manifest loaded: {manifest.get('version', 'unknown')}")
        
        # Step 3: Verify checksums
        print("🔐 Verifying file integrity...")
        for file_info in manifest.get('files', []):
            file_path = extract_dir / file_info['path']
            if not file_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing file: {file_info['path']}"
                )
            
            # Verify checksum
            if not soup_handler.validate_checksum(file_path, file_info['sha512']):
                raise HTTPException(
                    status_code=400,
                    detail=f"Checksum mismatch: {file_info['path']}"
                )
        
        print("✅ All checksums verified")
        
        # Step 4: Verify digital signature
        signature_path = extract_dir / "signature.sig"
        if not signature_path.exists():
            raise HTTPException(status_code=400, detail="Missing signature file")
        
        with open(signature_path, 'rb') as f:
            signature = f.read()
        
        # Load embedded public key
        public_key_path = Path(__file__).parent / "quorum_public.pem"
        if not public_key_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Security alert: SOUP public key 'quorum_public.pem' not found. Cannot verify update signature."
            )

        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        if not soup_handler.verify_signature(temp_package, signature, public_key):
            raise HTTPException(status_code=400, detail="Invalid SOUP package signature")
        
        print("✅ Signature verified successfully")
        
        # Step 5: Apply updates atomically
        print("🔄 Applying updates...")
        update_summary = {
            "models": [],
            "rules": [],
            "threat_intel": []
        }
        
        # Update AI models
        models_dir = extract_dir / "models"
        if models_dir.exists():
            for model_file in models_dir.iterdir():
                dest = MODELS_DIR / model_file.name
                shutil.copy2(model_file, dest)
                update_summary["models"].append(model_file.name)
                print(f"  ✅ Updated model: {model_file.name}")
        
        # Update parsing rules (if implemented)
        rules_dir = extract_dir / "rules"
        if rules_dir.exists():
            rules_dest = Path("backend/data/rules")
            rules_dest.mkdir(parents=True, exist_ok=True)
            for rule_file in rules_dir.iterdir():
                dest = rules_dest / rule_file.name
                shutil.copy2(rule_file, dest)
                update_summary["rules"].append(rule_file.name)
                print(f"  ✅ Updated rule: {rule_file.name}")
        
        # Update threat intelligence
        threat_intel_dir = extract_dir / "threat_intel"
        if threat_intel_dir.exists():
            intel_dest = Path("backend/data/threat_intel")
            intel_dest.mkdir(parents=True, exist_ok=True)
            for intel_file in threat_intel_dir.iterdir():
                dest = intel_dest / intel_file.name
                shutil.copy2(intel_file, dest)
                update_summary["threat_intel"].append(intel_file.name)
                print(f"  ✅ Updated threat intel: {intel_file.name}")
        
        # Step 6: Save update history
        update_info = {
            "timestamp": datetime.now().isoformat(),
            "version": manifest.get('version', 'unknown'),
            "package": file.filename,
            "status": "success",
            "summary": update_summary
        }
        save_update_history(update_info)
        
        # Cleanup
        temp_package.unlink()
        shutil.rmtree(extract_dir)
        
        return {
            "status": "success",
            "message": "SOUP update applied successfully",
            "version": manifest.get('version'),
            "applied_updates": update_summary,
            "timestamp": update_info["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Rollback on error (simplified - in production, use proper transaction management)
        print(f"❌ Update failed: {e}")
        
        # Save failed update to history
        update_info = {
            "timestamp": datetime.now().isoformat(),
            "package": file.filename,
            "status": "failed",
            "error": str(e)
        }
        save_update_history(update_info)
        
        raise HTTPException(
            status_code=500,
            detail=f"Update failed: {str(e)}"
        )

@router.get("/status")
async def get_soup_status():
    """Get current SOUP update status and history"""
    try:
        history = load_update_history()
        
        # Get current versions
        current_models = list(MODELS_DIR.glob("*.pkl")) + list(MODELS_DIR.glob("*.tflite"))
        
        return {
            "status": "operational",
            "current_models": [m.name for m in current_models],
            "last_update": history[-1] if history else None,
            "update_count": len(history),
            "recent_updates": history[-5:] if len(history) > 5 else history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_update_history(limit: int = 10):
    """Get update history"""
    try:
        history = load_update_history()
        return {
            "total_updates": len(history),
            "updates": history[-limit:] if len(history) > limit else history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback")
async def rollback_update(version: str):
    """
    Rollback to a previous version
    Note: This is a simplified implementation
    Production should maintain versioned backups
    """
    try:
        history = load_update_history()
        
        # Find the target version
        target_update = None
        for update in history:
            if update.get('version') == version:
                target_update = update
                break
        
        if not target_update:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")
        
        # In production, restore from backup
        # For now, just log the rollback attempt
        rollback_info = {
            "timestamp": datetime.now().isoformat(),
            "action": "rollback",
            "target_version": version,
            "status": "simulated"
        }
        save_update_history(rollback_info)
        
        return {
            "status": "success",
            "message": f"Rollback to version {version} simulated",
            "note": "Full rollback requires backup implementation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))