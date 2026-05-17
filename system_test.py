"""Comprehensive system test for KAAVAL video analysis."""
import cv2
import numpy as np
import requests
import time
from pathlib import Path

print("\n" + "="*70)
print("KAAVAL SYSTEM TEST - Video Analysis & Face Recognition")
print("="*70 + "\n")

# Test 1: Backend Health
print("[1/5] Checking Backend Health...")
try:
    r = requests.get('http://localhost:8000/healthz', timeout=5)
    if r.status_code == 200:
        print("✓ Backend is running and healthy")
    else:
        print(f"✗ Backend health check failed: {r.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Backend not accessible: {e}")
    exit(1)

# Test 2: Frontend Health
print("\n[2/5] Checking Frontend Health...")
try:
    r = requests.get('http://localhost:3000', timeout=5)
    if r.status_code == 200:
        print("✓ Frontend is running and serving")
    else:
        print(f"⚠ Frontend returned: {r.status_code}")
except Exception as e:
    print(f"⚠ Frontend may not be running: {e}")

# Test 3: Camera Status
print("\n[3/5] Checking Camera Service...")
try:
    r = requests.get('http://localhost:8000/api/camera/health')
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Camera service: {data.get('status', 'unknown')}")
        if data.get('status') == 'running':
            print(f"  - FPS: {data.get('fps', 0):.1f}")
    else:
        print(f"⚠ Camera health returned: {r.status_code}")
except Exception as e:
    print(f"⚠ Camera check failed: {e}")

# Test 4: Create & Upload Test Video with Synthetic Faces
print("\n[4/5] Testing Video Upload & Analysis...")

# Create synthetic video with circles (simulating faces)
output_path = Path("system_test_video.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

print(f"  Creating test video: {output_path}")
for i in range(60):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 50  # Dark background
    # Draw multiple circles to simulate faces
    cv2.circle(frame, (160, 240), 60, (200, 100, 0), -1)  # Blue circle
    cv2.circle(frame, (480, 240), 60, (0, 200, 100), -1)  # Green circle
    cv2.putText(frame, f'Frame {i}', (240, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    writer.write(frame)

writer.release()
file_size = output_path.stat().st_size / 1024
print(f"  ✓ Test video created ({file_size:.1f} KB)")

# Upload video
print("  Uploading video for analysis...")
with open(output_path, 'rb') as f:
    r = requests.post('http://localhost:8000/api/video/upload', files={'video_file': f})
    
if r.status_code == 202:
    data = r.json()
    job_id = data.get('job_id')
    print(f"  ✓ Upload accepted (202)")
    print(f"    Job ID: {job_id}")
    
    # Monitor progress
    print("  Monitoring progress...")
    completed = False
    for attempt in range(30):
        time.sleep(0.5)
        r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}')
        
        if r.status_code == 200:
            progress = r.json()
            status = progress.get('status')
            pct = progress.get('percent_complete', 0)
            
            if attempt % 2 == 0:  # Print every second
                print(f"    [{attempt*0.5:.1f}s] {status}: {pct:.0f}% complete")
            
            if status == 'completed':
                print(f"  ✓ Analysis completed in {attempt*0.5:.1f}s")
                completed = True
                break
        else:
            print(f"    Error checking progress: {r.status_code}")
            break
    
    if completed:
        # Get results
        print("\n[5/5] Retrieving Analysis Results...")
        r = requests.get(f'http://localhost:8000/api/video/results/{job_id}')
        
        if r.status_code == 200:
            results = r.json()
            num_detections = len(results.get('detections', []))
            print(f"✓ Results retrieved successfully")
            print(f"  - Detections found: {num_detections}")
            print(f"  - Total frames analyzed: {results.get('total_frames', 0)}")
            if results.get('matches'):
                print(f"  - Face matches: {len(results['matches'])}")
        else:
            print(f"⚠ Could not retrieve results: {r.status_code}")
    else:
        print(f"✗ Analysis did not complete within timeout")
else:
    print(f"✗ Upload failed: {r.status_code}")
    print(f"  Response: {r.text}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
