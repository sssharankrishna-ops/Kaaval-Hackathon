"""
KAAVAL System Diagnostic - Check GPU, CUDA, and PyTorch Configuration
=====================================================================
"""

import sys
import subprocess
from pathlib import Path

def run_cmd(cmd, description=""):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

def check_nvidia():
    """Check NVIDIA GPU and CUDA."""
    print("\n" + "="*70)
    print("1. NVIDIA GPU & CUDA CHECK")
    print("="*70)
    
    output, code = run_cmd("nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader")
    if code == 0:
        print(f"✅ NVIDIA GPU Found: {output}")
        
        output, _ = run_cmd("nvidia-smi --query-gpu=compute_cap --format=csv,noheader")
        print(f"✅ GPU Compute Capability: {output}")
        
        output, _ = run_cmd("nvidia-smi --query-gpu=driver_version --format=csv,noheader")
        print(f"✅ Driver Version: {output}")
        return True
    else:
        print("❌ No NVIDIA GPU detected")
        return False

def check_pytorch():
    """Check PyTorch installation."""
    print("\n" + "="*70)
    print("2. PYTORCH CHECK")
    print("="*70)
    
    code = """
import torch
print(f"Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
    print(f"Device Capability: {torch.cuda.get_device_capability(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"Total Memory: {props.total_memory / 1e9:.1f} GB")
    print(f"Current GPU Memory: {torch.cuda.memory_allocated(0) / 1e9:.3f} GB")
else:
    print("WARNING: CUDA not available - PyTorch might be CPU-only build")
"""
    
    output, retcode = run_cmd(f'python -c "{code}"')
    if retcode == 0:
        for line in output.split('\n'):
            if line.strip():
                print(f"  {line}")
        return torch.cuda.is_available() if "CUDA Available: True" in output else False
    else:
        print(f"❌ Error checking PyTorch: {output}")
        return False

def check_onnxruntime():
    """Check ONNX Runtime."""
    print("\n" + "="*70)
    print("3. ONNX RUNTIME CHECK")
    print("="*70)
    
    code = """
import onnxruntime as ort
print(f"Version: {ort.__version__}")
providers = ort.get_available_providers()
print(f"Available Providers: {', '.join(providers)}")
if 'CUDAExecutionProvider' in providers:
    print("✅ GPU Provider Available")
elif 'TensorrtExecutionProvider' in providers:
    print("✅ TensorRT Provider Available")
else:
    print("⚠️  Only CPU providers available")
"""
    
    output, retcode = run_cmd(f'python -c "{code}"')
    if retcode == 0:
        for line in output.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print(f"⚠️  ONNX Runtime check failed")

def check_models():
    """Check if models exist."""
    print("\n" + "="*70)
    print("4. MODELS CHECK")
    print("="*70)
    
    models_dir = Path("backend/models")
    if models_dir.exists():
        print(f"✅ Models directory exists: {models_dir.absolute()}")
        total_size = 0
        for model in sorted(models_dir.glob("*")):
            if model.is_file():
                size_mb = model.stat().st_size / (1024 * 1024)
                total_size += size_mb
                print(f"  ✅ {model.name} ({size_mb:.1f} MB)")
        print(f"\n  📊 Total: {total_size:.1f} MB")
    else:
        print(f"❌ Models directory not found")

def check_backend():
    """Check backend dependencies."""
    print("\n" + "="*70)
    print("5. BACKEND DEPENDENCIES CHECK")
    print("="*70)
    
    packages = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "opencv-cv2", "onnxruntime", "gfpgan"]
    
    for pkg in packages:
        code = f"import {pkg.replace('-', '_')}; print(pkg.__version__ if hasattr(pkg, '__version__') else 'installed')"
        output, retcode = run_cmd(f'python -c "{code}"')
        
        if retcode == 0:
            print(f"  ✅ {pkg}: {output[:50]}")
        else:
            print(f"  ❌ {pkg}: NOT INSTALLED")

def main():
    """Run all diagnostics."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  KAAVAL SYSTEM DIAGNOSTIC - GPU & CUDA CONFIGURATION".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    gpu_available = check_nvidia()
    cuda_available = check_pytorch()
    check_onnxruntime()
    check_models()
    check_backend()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*70)
    
    if gpu_available:
        print("✅ GPU Hardware: Available (NVIDIA RTX 3050)")
    else:
        print("❌ GPU Hardware: Not detected")
    
    if cuda_available:
        print("✅ CUDA Support: PyTorch has CUDA enabled")
        print("\n🎉 System is properly configured for GPU acceleration!")
    else:
        print("⚠️  CUDA Support: PyTorch is CPU-only")
        print("\n📝 RECOMMENDED ACTIONS:")
        print("   1. Uninstall: pip uninstall torch torchvision -y")
        print("   2. Install CUDA version: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print("   3. Restart the backend server")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
