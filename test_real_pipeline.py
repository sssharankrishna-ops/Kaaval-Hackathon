#!/usr/bin/env python
"""Test real data processing pipeline."""

import requests
import cv2
import numpy as np
import time

# Create test image
test_img = np.ones((200, 200, 3), dtype=np.uint8) * 128
for i in range(50, 150):
    cv2.circle(test_img, (100, 100), 30, (255, 100, 100), -1)
cv2.imwrite('test_real_face.jpg', test_img)

print('🔄 Testing REAL DATA PROCESSING')
print('=' * 50)

# Test restoration
print('\n[1] Face Restoration...')
with open('test_real_face.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/api/image/restore', files={'image': f})
    if r.status_code == 200:
        data = r.json()
        print(f'✅ Status: {r.status_code}')
        path = data["restored_image_path"][:80]
        print(f'   Restored image: {path}...')
    else:
        print(f'❌ Error: {r.status_code}')

# Test age progression
print('\n[2] Age Progression with REAL IMAGE...')
with open('test_real_face.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/api/image/age_progression', files={'image': f})
    if r.status_code == 200:
        data = r.json()
        print(f'✅ Status: {r.status_code}')
        print(f'   Job ID: {data["job_id"]}')
        print(f'   Status: {data["status"]}')
        print(f'   Variants queued: {len(data.get("variants", []))} items')
        time.sleep(2)
        # Get results
        job_id = data['job_id']
        r2 = requests.get(f'http://localhost:8000/api/image/age_progression/{job_id}')
        if r2.status_code == 200:
            results = r2.json()
            variants = results.get("variants", [])
            print(f'   After processing: {len(variants)} variants generated')
            if variants:
                for v in variants[:2]:
                    p = v["image_path"][:60]
                    print(f'     - Age +{v["age_offset"]}: {p}...')
    else:
        print(f'❌ Error: {r.status_code} - {r.text[:200]}')

print('\n✅ All tests complete!')
