"""Diagnostic: Check Current Job Status & System Performance"""
import requests
import json
import psutil
from pathlib import Path

print("\n" + "="*70)
print("SYSTEM DIAGNOSTICS - CURRENT STATUS")
print("="*70 + "\n")

# 1. Check system resources
print("[1/4] System Resources:")
cpu_percent = psutil.cpu_percent(interval=0.5)
memory = psutil.virtual_memory()
gpu_procs = []

try:
    import torch
    if torch.cuda.is_available():
        gpu_mem = torch.cuda.memory_allocated() / (1024**3)
        gpu_max = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  CPU: {cpu_percent}%")
        print(f"  RAM: {memory.percent}% ({memory.available / (1024**3):.1f}GB free)")
        print(f"  GPU: {gpu_mem:.1f}GB / {gpu_max:.1f}GB")
except:
    pass

# 2. Check running Python processes
print("\n[2/4] Running Python Processes:")
for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
    if 'python' in proc.name().lower():
        print(f"  PID {proc.pid}: {proc.memory_percent():.1f}% memory")

# 3. Check uploads directory
print("\n[3/4] Recent Uploads:")
uploads_dir = Path("backend/uploads")
if uploads_dir.exists():
    files = sorted(list(uploads_dir.glob("*")), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    for f in files:
        size_mb = f.stat().st_size / (1024*1024)
        print(f"  {f.name}: {size_mb:.1f}MB")
else:
    print("  No uploads directory")

# 4. Check backend endpoints and active jobs
print("\n[4/4] Backend Job Status:")
try:
    # Try to get any active video jobs
    r = requests.get('http://localhost:8000/api/video/progress/all', timeout=5)
    if r.status_code != 404:
        print(f"  Active video jobs: {r.json()}")
    else:
        print("  Active video jobs: Endpoint not available")
except Exception as e:
    print(f"  Could not check job status: {e}")

print("\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)
print("""
If processing is stuck:
1. RESTART BACKEND: Stop-Job -Name Backend; Start new Backend job
2. CHECK ATTRIBUTES: Attribute model has dimension mismatch errors
3. REDUCE VIDEO: Use shorter videos (< 1 minute) for testing
4. MONITOR GPU: Ensure GPU memory not full (max 6GB on RTX 3050)
5. CHECK UPLOADS: Verify video file is valid MP4

QUICK FIX - Clear stuck jobs and restart:
  - Delete backend/uploads/* (clear uploaded files)
  - Stop-Job -Name Backend
  - Start new Backend job
""")

print("="*70 + "\n")
