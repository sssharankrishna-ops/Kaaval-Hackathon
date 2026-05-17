"""Video Analysis Output Location & Module Status Check"""
import requests
import json
from pathlib import Path

print("\n" + "="*80)
print("VIDEO ANALYSIS OUTPUT & MODULE STATUS")
print("="*80 + "\n")

print("📍 WHERE DOES VIDEO ANALYSIS OUTPUT GET DISPLAYED?")
print("-" * 80)
print("""
1. FRONTEND WEB INTERFACE (http://localhost:3000):
   • Upload video with reference image
   • See progress bar in real-time
   • When complete → Results panel shows:
     - Timeline of detected faces
     - Person matches and confidence scores
     - Timestamps for each detection
     - Face thumbnails with bounding boxes

2. API ENDPOINTS (for programmatic access):
   
   a) Progress Endpoint:
      GET /api/video/progress/{job_id}
      Returns: { status, percent_complete, processed_frames, total_frames }
      
   b) Results Endpoint:
      GET /api/video/results/{job_id}
      Returns: { detections, matches, timeline, duration }
      
   c) Frames Endpoint:
      GET /api/video/frames/{job_id}
      Returns: Detailed frame-by-frame extraction with timestamps

3. UPLOADED FILES LOCATION:
   backend/uploads/  → All uploaded videos and extracted frames
   
4. DATABASE STORAGE:
   backend/database/kaaval.db  → Analysis results stored permanently
""")

print("\n" + "="*80)
print("🔧 MODULE STATUS CHECK")
print("-" * 80)

# Check modules
modules_status = {
    "Reconstruction": {
        "file": "backend/app/ml/reconstruction/encoder.py",
        "purpose": "Encode faces to latent vectors for age progression"
    },
    "Age Progression": {
        "file": "backend/app/ml/age_progression/stylegan.py",
        "purpose": "Generate age-progressed face variants (+0, +10, +20, +30 years)"
    },
    "Video Pipeline": {
        "file": "backend/app/pipelines/video_pipeline.py",
        "purpose": "Process uploaded videos frame-by-frame"
    },
}

for module, details in modules_status.items():
    path = Path(details["file"])
    exists = path.exists()
    status_icon = "✅" if exists else "❌"
    print(f"\n{status_icon} {module}")
    print(f"   Purpose: {details['purpose']}")
    print(f"   File: {details['file']}")
    if exists:
        size_kb = path.stat().st_size / 1024
        print(f"   Size: {size_kb:.1f} KB")

print("\n" + "="*80)
print("TEST VIDEO ANALYSIS OUTPUT")
print("-" * 80 + "\n")

# Create test and show output flow
import cv2
import numpy as np
import time

output_path = Path("output_test.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

print("[1/3] Creating test video...")
for i in range(5):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
    cv2.circle(frame, (320, 240), 80, (0, 255, 0), -1)
    cv2.putText(frame, f'Test {i}', (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    writer.write(frame)
writer.release()
print(f"✓ Created: {output_path.stat().st_size / 1024:.1f} KB\n")

print("[2/3] Uploading and processing...")
with open(output_path, 'rb') as f:
    r = requests.post('http://localhost:8000/api/video/upload', files={'video_file': f})

if r.status_code == 202:
    data = r.json()
    job_id = data['job_id']
    print(f"✓ Job ID: {job_id}")
    
    # Wait for completion
    for attempt in range(20):
        time.sleep(0.5)
        r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}')
        if r.status_code == 200:
            progress = r.json()
            if progress['status'] == 'completed':
                print(f"✓ Processing complete\n")
                break
    
    print("[3/3] VIDEO ANALYSIS OUTPUT FLOW:\n")
    
    # Show progress response
    print("A) PROGRESS RESPONSE (during processing):")
    r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}')
    progress_data = r.json()
    print(f"""   GET /api/video/progress/{job_id}
   
   Response:
   {{
     "job_id": "{progress_data['job_id']}",
     "status": "{progress_data['status']}",
     "processed_frames": {progress_data['processed_frames']},
     "total_frames": {progress_data['total_frames']},
     "percent_complete": {progress_data['percent_complete']}
   }}
""")
    
    # Show results response
    print("\nB) RESULTS RESPONSE (when complete):")
    r = requests.get(f'http://localhost:8000/api/video/results/{job_id}')
    if r.status_code == 200:
        results_data = r.json()
        print(f"""   GET /api/video/results/{job_id}
   
   Response:
   {{
     "job_id": "{results_data.get('job_id', job_id)}",
     "total_frames": {results_data.get('total_frames', 0)},
     "detections": {len(results_data.get('detections', []))} faces found,
     "matches": {len(results_data.get('matches', []))} person matches,
     "timeline": {len(results_data.get('timeline', []))} timeline events
   }}
""")
        
        if results_data.get('matches'):
            print("   Sample matches:")
            for match in results_data.get('matches', [])[:3]:
                print(f"""     - {match.get('person_name', 'Unknown')}: 
        Confidence: {match.get('confidence', 0):.2%}""")
    else:
        print(f"   Status: {r.status_code}")
    
    # Show frames endpoint
    print("\nC) FRAMES ENDPOINT (detailed timeline):")
    r = requests.get(f'http://localhost:8000/api/video/frames/{job_id}')
    if r.status_code == 200:
        frames_data = r.json()
        print(f"""   GET /api/video/frames/{job_id}
   
   Response:
   {{
     "job_id": "{frames_data['job_id']}",
     "total_frames": {frames_data['total_frames']},
     "frames": [
""")
        for frame in frames_data.get('frames', [])[:3]:
            print(f"""       {{
         "frame_number": {frame['frame_number']},
         "timestamp": {frame['timestamp']:.2f}s,
         "confidence": {frame['confidence']:.2%},
         "person_name": "{frame['person_name']}"
       }},""")
        if len(frames_data.get('frames', [])) > 3:
            print(f"       ... {len(frames_data.get('frames', [])) - 3} more frames")
        print("     ]")
        print("   }")

print("\n" + "="*80)
print("✅ OUTPUT DISPLAY COMPLETE")
print("="*80)

print("""
HOW TO VIEW RESULTS:

1. REAL-TIME (Frontend):
   → Visit http://localhost:3000
   → Upload video
   → Watch progress bar
   → See results when complete

2. API CALLS (Programmatic):
   → Check /api/video/progress/{job_id} while processing
   → Get /api/video/results/{job_id} when done
   → Use /api/video/frames/{job_id} for detailed timeline

3. RECONSTRUCTION & AGE PROGRESSION:
   → Not used in video analysis (only for single images)
   → Access via /api/image/restore (face restoration)
   → Access via /api/image/age_progression (age variants)
""")
print("\n")
