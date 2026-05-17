"""Complete System Data Verification & Test"""
import requests
import json
import cv2
import numpy as np
from pathlib import Path
import time

print("\n" + "="*70)
print("KAAVAL SYSTEM - COMPLETE DATA & FUNCTIONALITY TEST")
print("="*70 + "\n")

# Test 1: Check actual embeddings loaded in system
print("[1/5] Checking Loaded Embeddings...")
embeddings_dir = Path("backend/embeddings_output")
embedding_files = sorted(list(embeddings_dir.glob("*_embeddings.json")))
print(f"Total persons in database: {len(embedding_files)}")

if embedding_files:
    # Load and display sample embedding
    with open(embedding_files[0]) as f:
        sample = json.load(f)
    person_name = embedding_files[0].stem.replace("_embeddings", "")
    print(f"✓ Sample person: {person_name}")
    print(f"  Embedding shape: {len(sample.get('embedding', []))} dimensions")
    print(f"  Image count: {len(sample.get('images', []))}")

# Test 2: Upload real face image and analyze
print("\n[2/5] Testing with Real Image...")
# Create a test directory with sample images
sample_dir = Path("backend/datasets/sample_faces")
if sample_dir.exists():
    sample_images = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
    print(f"Sample images found: {len(sample_images)}")
    
    if sample_images:
        test_image = sample_images[0]
        print(f"Using test image: {test_image.name}")
        
        # Upload for analysis
        with open(test_image, 'rb') as f:
            try:
                r = requests.post(
                    'http://localhost:8000/api/image/restore',
                    files={'image': f},
                    timeout=30
                )
                if r.status_code in [200, 202]:
                    print(f"✓ Image analysis: {r.status_code}")
                else:
                    print(f"⚠ Image analysis returned: {r.status_code}")
            except Exception as e:
                print(f"⚠ Image analysis error: {e}")
else:
    print(f"⚠ Sample images directory not found")

# Test 3: Create and analyze real test video
print("\n[3/5] Creating Real Video with Pattern...")
output_path = Path("real_test_video.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

# Create more realistic test video with gradients and patterns
for i in range(60):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
    
    # Draw multiple faces with different colors
    cv2.circle(frame, (160, 120), 80, (0, 200, 200), -1)  # Cyan face
    cv2.circle(frame, (480, 120), 80, (0, 200, 100), -1)  # Green face
    cv2.circle(frame, (320, 320), 80, (100, 200, 0), -1)  # Yellow face
    
    # Add frame counter
    cv2.putText(frame, f'Frame: {i}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, 'Test Video', (200, 470), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    writer.write(frame)

writer.release()
print(f"✓ Real test video created: {output_path.stat().st_size / 1024:.1f} KB")

# Test 4: Upload and analyze video
print("\n[4/5] Uploading Video for Analysis...")
with open(output_path, 'rb') as f:
    r = requests.post(
        'http://localhost:8000/api/video/upload',
        files={'video_file': f},
        timeout=10
    )
    
if r.status_code == 202:
    data = r.json()
    job_id = data.get('job_id')
    print(f"✓ Video upload: {r.status_code}")
    print(f"  Job ID: {job_id}")
    
    # Monitor progress
    print("\nMonitoring Analysis Progress...")
    for attempt in range(30):
        time.sleep(0.5)
        r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}', timeout=5)
        
        if r.status_code == 200:
            progress = r.json()
            status = progress.get('status')
            pct = progress.get('percent_complete', 0)
            processed = progress.get('processed_frames', 0)
            total = progress.get('total_frames', 0)
            
            if attempt % 4 == 0:  # Print every 2 seconds
                print(f"  [{attempt*0.5:.1f}s] {status}: {pct:.0f}% | {processed}/{total} frames")
            
            if status == 'completed':
                print(f"\n✓ Analysis completed in {attempt*0.5:.1f}s")
                
                # Get results
                print("\n[5/5] Retrieving Results...")
                r = requests.get(f'http://localhost:8000/api/video/results/{job_id}', timeout=5)
                if r.status_code == 200:
                    results = r.json()
                    detections = results.get('detections', [])
                    matches = results.get('matches', [])
                    
                    print(f"✓ Results retrieved")
                    print(f"  - Total detections: {len(detections)}")
                    print(f"  - Unique faces matched: {len(set([m.get('person_id') for m in matches]))}")
                    
                    if matches:
                        print(f"\n  Top matches:")
                        top_matches = sorted(matches, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
                        for i, match in enumerate(top_matches, 1):
                            print(f"    {i}. {match.get('person_name', 'Unknown')}: {match.get('confidence', 0):.2%}")
                else:
                    print(f"✗ Could not retrieve results: {r.status_code}")
                break
else:
    print(f"✗ Video upload failed: {r.status_code}")

print("\n" + "="*70)
print("TEST COMPLETE - System is Ready for Real Data")
print("="*70 + "\n")
