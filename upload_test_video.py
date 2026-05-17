import cv2
import numpy as np
import requests
from pathlib import Path

# Create a new test video with visible faces
output_path = Path('test_video_v2.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (640, 480))

# Create 60 frames with a simple pattern
for i in range(60):
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.circle(frame, (320, 240), 100, (0, 0, 255), -1)
    cv2.putText(frame, f'Frame {i}', (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    writer.write(frame)

writer.release()
print(f'Created test video at {output_path}')
print(f'File size: {output_path.stat().st_size / 1024:.1f} KB')

# Upload the video for analysis
with open(output_path, 'rb') as f:
    response = requests.post('http://localhost:8000/api/video/upload', files={'video_file': f})
    print(f'Upload response: {response.status_code}')
    data = response.json()
    job_id = data.get('job_id')
    print(f'Job ID: {job_id}')
    status = data.get('status')
    print(f'Status: {status}')
    
    # Monitor progress
    import time
    time.sleep(2)
    response = requests.get(f'http://localhost:8000/api/video/progress/{job_id}')
    progress = response.json()
    print(f'\nProgress after 2s: {progress}')
