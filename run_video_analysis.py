import cv2
import numpy as np
import requests
from pathlib import Path
import time

# Create a test video
output_path = Path('test_video_final.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

# Create 60 frames
for i in range(60):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
    cv2.circle(frame, (320, 240), 100, (0, 255, 0), -1)
    cv2.putText(frame, f'Frame {i}', (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    writer.write(frame)

writer.release()
print(f'Created: {output_path}')
print(f'Size: {output_path.stat().st_size / 1024:.1f} KB')

# Upload
with open(output_path, 'rb') as f:
    r = requests.post('http://localhost:8000/api/video/upload', files={'video_file': f})
    print(f'Status: {r.status_code}')
    data = r.json()
    job_id = data.get('job_id')
    print(f'Job ID: {job_id}')
    
    # Monitor progress - wait longer this time
    for attempt in range(20):
        time.sleep(1)
        r = requests.get(f'http://localhost:8000/api/video/progress/{job_id}')
        if r.status_code == 200:
            progress = r.json()
            print(f'[{attempt+1}s] Status: {progress.get("status")}, Progress: {progress.get("percent_complete")}%, Frames: {progress.get("processed_frames")}/{progress.get("total_frames")}')
            if progress.get('status') == 'completed':
                print('\nAnalysis complete! Getting results...')
                r = requests.get(f'http://localhost:8000/api/video/results/{job_id}')
                if r.status_code == 200:
                    results = r.json()
                    print(f'Results found with {len(results.get("detections", []))} detections')
                break
        else:
            print(f'[{attempt+1}s] Job not found: {r.status_code}')
