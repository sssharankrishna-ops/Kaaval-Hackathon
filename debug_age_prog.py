#!/usr/bin/env python
"""Detailed debugging of age progression pipeline."""

import requests
import cv2
import numpy as np
import time
import json
from pathlib import Path

# Create test image
test_img = np.ones((200, 200, 3), dtype=np.uint8) * 128
cv2.circle(test_img, (100, 100), 40, (255, 100, 100), -1)
cv2.imwrite('test_debug.jpg', test_img)

print('🔍 DEBUGGING AGE PROGRESSION PIPELINE')
print('=' * 60)

# Step 1: Upload image for age progression
print('\n[STEP 1] POST /api/image/age_progression')
with open('test_debug.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/api/image/age_progression', files={'image': f})
    print(f'Status: {r.status_code}')
    data = r.json()
    print(f'Response: {json.dumps(data, indent=2)}')
    job_id = data['job_id']

# Step 2: Wait for background processing
print(f'\n[STEP 2] Waiting 3 seconds for background processing...')
time.sleep(3)

# Step 3: Check if images were created
print(f'\n[STEP 3] Checking if age variant images exist...')
uploads_dir = Path('backend/uploads')
reports_dir = Path('backend/reports')

print(f'Uploads dir: {uploads_dir.exists()}')
if uploads_dir.exists():
    jpg_files = list(uploads_dir.glob('*.jpg'))
    print(f'  JPG files: {len(jpg_files)}')
    png_files = list(uploads_dir.glob('*.png'))
    print(f'  PNG files: {len(png_files)}')

print(f'Reports dir: {reports_dir.exists()}')
if reports_dir.exists():
    age_variants = list(reports_dir.glob(f'{job_id}_age_*.png'))
    print(f'  Age variant images: {len(age_variants)}')
    for img in age_variants:
        print(f'    - {img.name}')

# Step 4: Try to GET the results
print(f'\n[STEP 4] GET /api/image/age_progression_result/{job_id}')
r = requests.get(f'http://localhost:8000/api/image/age_progression_result/{job_id}')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Response: {json.dumps(data, indent=2)}')

# Step 5: Try to serve one of the images
if data.get('variants'):
    variant = data['variants'][0]
    img_path = variant['image_path']
    print(f'\n[STEP 5] Serving image via /api/image/file/')
    print(f'  Image path: {img_path}')
    r = requests.get(f'http://localhost:8000/api/image/file/{requests.utils.quote(img_path, safe="")}')
    print(f'  Status: {r.status_code}')
    print(f'  Content-Type: {r.headers.get("content-type")}')
    print(f'  Size: {len(r.content)} bytes')

print('\n✅ Debug complete!')
