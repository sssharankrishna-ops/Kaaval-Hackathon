"""Project Configuration & Data Verification Diagnostic"""
import requests
import json
from pathlib import Path

print("\n" + "="*70)
print("KAAVAL PROJECT CONFIGURATION & DATA VERIFICATION")
print("="*70 + "\n")

# 1. Check Database
print("[1/6] Checking Database...")
db_path = Path("backend/database/kaaval.db")
if db_path.exists():
    size_mb = db_path.stat().st_size / (1024*1024)
    print(f"✓ Database exists: {db_path}")
    print(f"  Size: {size_mb:.1f} MB")
else:
    print(f"✗ Database not found at {db_path}")

# 2. Check Embeddings
print("\n[2/6] Checking Embeddings...")
embeddings_dir = Path("backend/embeddings_output")
if embeddings_dir.exists():
    npy_files = list(embeddings_dir.glob("*.npy"))
    json_files = list(embeddings_dir.glob("*.json"))
    print(f"✓ Embeddings directory exists")
    print(f"  NPY files (vectors): {len(npy_files)}")
    print(f"  JSON files (metadata): {len(json_files)}")
    if json_files:
        print(f"  Sample: {json_files[0].name}")
else:
    print(f"✗ Embeddings directory not found")

# 3. Check FAISS Index
print("\n[3/6] Checking FAISS Index...")
faiss_index = Path("backend/models/faiss/embeddings.index")
if faiss_index.exists():
    size_mb = faiss_index.stat().st_size / (1024*1024)
    print(f"✓ FAISS index exists: {faiss_index}")
    print(f"  Size: {size_mb:.1f} MB")
else:
    print(f"✗ FAISS index not found")

# 4. Check ML Models
print("\n[4/6] Checking ML Models...")
models_dir = Path("backend/models")
models = {
    "retinaface.onnx": "Face Detection",
    "arcface_resnet100.onnx": "Face Recognition",
    "attribute_net.onnx": "Attribute Detection",
    "gfpgan.pth": "Face Restoration",
}
for model, desc in models.items():
    model_path = models_dir / model
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024*1024)
        print(f"✓ {desc}: {size_mb:.1f} MB")
    else:
        print(f"✗ {desc}: NOT FOUND")

# 5. Check Backend Configuration
print("\n[5/6] Checking Backend Configuration...")
config_path = Path("backend/app/core/config.py")
if config_path.exists():
    print(f"✓ Configuration file exists")
    with open(config_path) as f:
        content = f.read()
        if "use_gpu" in content:
            print(f"  GPU support: Configured")
        if "frame_skip" in content:
            print(f"  Frame skipping: Configured")
else:
    print(f"✗ Configuration not found")

# 6. Test Backend Endpoints
print("\n[6/6] Testing Backend Endpoints...")
try:
    # Health check
    r = requests.get('http://localhost:8000/healthz', timeout=5)
    print(f"✓ Health endpoint: {r.status_code}")
    
    # Camera status
    r = requests.get('http://localhost:8000/api/camera/health', timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Camera service: {data.get('status', 'unknown')}")
    
    # Database info
    r = requests.get('http://localhost:8000/api/database/info', timeout=5)
    if r.status_code == 200:
        data = r.json()
        embeddings = data.get('total_embeddings', 0)
        print(f"✓ Database API: {embeddings} embeddings loaded")
    else:
        print(f"⚠ Database endpoint: {r.status_code}")
        
except Exception as e:
    print(f"✗ Backend communication error: {e}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70 + "\n")

print("Next Steps:")
print("1. If embeddings < 100: Run embedding extraction")
print("2. If models missing: Download from model repository")
print("3. If backend endpoint issues: Restart backend service")
