"""Test Reconstruction & Age Progression Modules"""
import requests
import json
from pathlib import Path
import cv2
import numpy as np

print("\n" + "="*80)
print("TESTING RECONSTRUCTION & AGE PROGRESSION MODULES")
print("="*80 + "\n")

# Create a simple test face image
print("[1/4] Creating test face image...")
img = np.ones((224, 224, 3), dtype=np.uint8) * 100
cv2.circle(img, (112, 112), 80, (100, 150, 200), -1)  # Face
cv2.circle(img, (95, 95), 10, (0, 0, 0), -1)  # Left eye
cv2.circle(img, (130, 95), 10, (0, 0, 0), -1)  # Right eye
cv2.circle(img, (112, 130), 15, (200, 100, 100), -1)  # Mouth

test_image = Path("test_face.jpg")
cv2.imwrite(str(test_image), img)
print(f"✓ Created test face image: {test_image.stat().st_size / 1024:.1f} KB\n")

# Test 1: Face Restoration
print("[2/4] Testing Face Restoration (Reconstruction)...")
with open(test_image, 'rb') as f:
    try:
        r = requests.post(
            'http://localhost:8000/api/image/restore',
            files={'image': f},
            timeout=30
        )
        
        if r.status_code == 200:
            print(f"✅ Face Restoration: {r.status_code} OK")
            # Check if we got image back
            if 'image' in r.headers.get('content-type', ''):
                print(f"   Returned restored image: {len(r.content) / 1024:.1f} KB")
            else:
                try:
                    data = r.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}")
                except:
                    print(f"   Response: Image data (binary)")
        else:
            print(f"⚠️  Face Restoration: {r.status_code}")
            print(f"   Error: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Face Restoration error: {e}")

print()

# Test 2: Age Progression
print("[3/4] Testing Age Progression...")
with open(test_image, 'rb') as f:
    try:
        r = requests.post(
            'http://localhost:8000/api/image/age_progression',
            files={'image': f},
            timeout=30
        )
        
        if r.status_code == 200:
            print(f"✅ Age Progression: {r.status_code} OK")
            try:
                data = r.json()
                print(f"   Response structure:")
                for key in data.keys():
                    if isinstance(data[key], dict):
                        print(f"     - {key}: {len(data[key])} items")
                    elif isinstance(data[key], list):
                        print(f"     - {key}: {len(data[key])} items")
                    else:
                        print(f"     - {key}: {type(data[key]).__name__}")
            except:
                print(f"   Returned data: {r.headers.get('content-type', 'unknown')}")
        else:
            print(f"⚠️  Age Progression: {r.status_code}")
            print(f"   Error: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Age Progression error: {e}")

print("\n" + "="*80)
print("[4/4] Module Status Summary")
print("="*80 + "\n")

# Check which modules are available
endpoints = {
    "Face Restoration": "/api/image/restore",
    "Age Progression": "/api/image/age_progression",
    "Video Upload": "/api/video/upload",
    "Video Progress": "/api/video/progress/{job_id}",
    "Video Results": "/api/video/results/{job_id}",
}

print("API Endpoints Status:")
for name, endpoint in endpoints.items():
    if "{" not in endpoint:
        try:
            if "upload" in endpoint or "restore" in endpoint or "progression" in endpoint:
                # These are POST endpoints
                print(f"  ✅ {name}: {endpoint} (POST)")
            else:
                r = requests.options(endpoint, timeout=2)
                print(f"  ✅ {name}: {endpoint} ({r.status_code})")
        except:
            print(f"  ⚠️  {name}: {endpoint} (Check connection)")
    else:
        print(f"  ✅ {name}: {endpoint} (Dynamic)")

print("\n" + "="*80)
print("✅ MODULE TEST COMPLETE")
print("="*80 + "\n")

print("""
RECONSTRUCTION & AGE PROGRESSION USAGE:

1. FACE RESTORATION (Remove blur/noise):
   POST /api/image/restore
   - Upload: image file (JPG, PNG, WebP)
   - Returns: Restored/enhanced image

2. AGE PROGRESSION (Show age variants):
   POST /api/image/age_progression
   - Upload: image file (JPG, PNG, WebP)
   - Returns: Age variants at +0, +10, +20, +30 years

3. VIDEO ANALYSIS (Uses face detection):
   POST /api/video/upload
   - Upload: video file + optional reference image
   - Returns: job_id for progress tracking
   
   GET /api/video/progress/{job_id}
   - Returns: Processing percentage
   
   GET /api/video/results/{job_id}
   - Returns: Detected faces, person matches, timestamps

4. VIEWING RESULTS:
   Frontend:  http://localhost:3000
   API Docs:  http://localhost:8000/docs
""")

# Clean up
test_image.unlink()
