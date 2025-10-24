"""
Verify backend is ready for offline deployment
Checks all dependencies are bundled and no runtime internet access needed
"""

import sys
import importlib
from pathlib import Path


def check_required_packages():
    """Verify all required packages are installed"""
    required = [
        'fastapi',
        'uvicorn',
        'duckdb',
        'polars',
        'scikit-learn',
        'pyod',
        'joblib',
        'cryptography',
        'paramiko',  # Optional for SSH
        'pywinrm',   # Optional for Windows
    ]
    
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - NOT INSTALLED")
    
    return missing


def check_ai_models():
    """Verify AI models are present"""
    from config import MODELS_DIR
    
    required_models = [
        MODELS_DIR / "iforest_model.pkl",
        MODELS_DIR / "tfidf_vectorizer.pkl"
    ]
    
    missing = []
    for model_path in required_models:
        if model_path.exists():
            print(f"✅ {model_path.name}")
        else:
            missing.append(model_path.name)
            print(f"❌ {model_path.name} - NOT FOUND")
    
    return missing


def check_soup_keys():
    """Verify SOUP encryption keys are configured"""
    import os
    
    keys_required = ['ENCRYPTION_KEY', 'SOUP_SIGNING_KEY']
    missing = []
    
    for key in keys_required:
        if os.getenv(key):
            print(f"✅ {key} configured")
        else:
            missing.append(key)
            print(f"❌ {key} - NOT SET")
    
    return missing


def check_external_dependencies():
    """Check for hardcoded external URLs"""
    backend_dir = Path(__file__).parent.parent
    
    # Patterns that indicate external dependencies
    external_patterns = [
        'http://',
        'https://',
        'requests.get',
        'requests.post',
        'urllib.request',
    ]
    
    issues = []
    
    for py_file in backend_dir.rglob("*.py"):
        if "test" in py_file.name or "venv" in str(py_file):
            continue
        
        content = py_file.read_text()
        
        for pattern in external_patterns:
            if pattern in content and "localhost" not in content:
                # Check if it's in a comment
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not line.strip().startswith('#'):
                        issues.append(f"{py_file.name}:{i+1} - {line.strip()[:60]}")
    
    return issues


def main():
    print("=" * 70)
    print("🔍 PROJECT QUORUM - OFFLINE READINESS VERIFICATION")
    print("=" * 70)
    
    print("\n📦 Checking Python packages...")
    missing_packages = check_required_packages()
    
    print("\n🤖 Checking AI models...")
    missing_models = check_ai_models()
    
    print("\n🔐 Checking security keys...")
    missing_keys = check_soup_keys()
    
    print("\n🌐 Checking for external dependencies...")
    external_deps = check_external_dependencies()
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    all_good = True
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print(f"   Install: pip install {' '.join(missing_packages)}")
        all_good = False
    else:
        print("✅ All required packages installed")
    
    if missing_models:
        print(f"❌ Missing AI models: {', '.join(missing_models)}")
        print(f"   Train models or copy from training system")
        all_good = False
    else:
        print("✅ All AI models present")
    
    if missing_keys:
        print(f"❌ Missing environment keys: {', '.join(missing_keys)}")
        print(f"   Set in .env file")
        all_good = False
    else:
        print("✅ Security keys configured")
    
    if external_deps:
        print(f"⚠️ Potential external dependencies found:")
        for dep in external_deps[:5]:  # Show first 5
            print(f"   - {dep}")
        if len(external_deps) > 5:
            print(f"   ... and {len(external_deps) - 5} more")
        all_good = False
    else:
        print("✅ No external dependencies detected")
    
    print("\n" + "=" * 70)
    if all_good:
        print("✅ SYSTEM IS READY FOR OFFLINE DEPLOYMENT")
    else:
        print("❌ SYSTEM IS NOT READY - ADDRESS ISSUES ABOVE")
    print("=" * 70)
    
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())