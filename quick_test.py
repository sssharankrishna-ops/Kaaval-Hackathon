"""Test with Short Real Video - Fixed Processing"""
import requests
import json
import cv2
import numpy as np
from pathlib import Path
import time

print("\n" + "="*70)
print("FRESH START - SHORT VIDEO TEST")
print("="*70 + "\n")

# Create a SHORT test video (10 frames = 0.5 seconds at 20 FPS)
output_path = Path("quick_test.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

print("[1/4] Creating SHORT test video (0.5 seconds)...")
for i in range(10):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 50
    cv2.circle(frame, (320, 240), 100, (0, 255, 0), -1)
    cv2.putText(frame, f'Frame {i}', (240, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    writer.write(frame)

writer.release()
size_kb = output_path.stat().st_size / 1024
print(f"✓ Created: {size_kb:.1f} KB\n")

print("[2/4] Uploading video...")
with open(output_path, 'rb') as f:
    r = requests.post('http://localhost:8000/api/video/upload', files={'video_file': f}, timeout=10)

if r.status_code == 202:
    data = r.json()
    job_id = data.get('job_id')
    print(f"✓ Upload accepted: {job_id}\n")
    
    print("[3/4] Monitoring real-time progress...")
    start = time.time()
    for attempt in range(60):  # 60 * 0.5s = 30 second timeout
        time.sleep(0.5)
        r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}', timeout=5)
        
        if r.status_code == 200:
            progress = r.json()
            status = progress.get('status')
            pct = progress.get('percent_complete', 0)
            processed = progress.get('processed_frames', 0)
            total = progress.get('total_frames', 0)
            
            # Print progress every second
            if attempt % 2 == 0:
                elapsed = time.time() - start
                print(f"  [{elapsed:.1f}s] {status}: {pct:.0f}% | {processed}/{total} frames")
            
            if status == 'completed':
                elapsed = time.time() - start
                print(f"\n✓ Analysis COMPLETE in {elapsed:.1f}s!\n")
                
                print("[4/4] Retrieving results...")
                r = requests.get(f'http://localhost:8000/api/video/results/{job_id}', timeout=5)
                if r.status_code == 200:
                    results = r.json()
                    print(f"✓ Results retrieved:")
                    print(f"  - Total detections: {len(results.get('detections', []))}")
                    print(f"  - Face matches: {len(results.get('matches', []))}")
                    print(f"  - Timeline events: {len(results.get('timeline', []))}")
                break
        else:
            if attempt % 4 == 0:
                print(f"  Error: {r.status_code}")
else:
    print(f"✗ Upload failed: {r.status_code}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
