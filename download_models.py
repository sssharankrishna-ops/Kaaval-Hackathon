"""Download required models for KAAVAL system."""

import os
import urllib.request
import shutil
from pathlib import Path

# Model URLs - using reliable sources
MODELS = {
    "gfpgan.pth": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
}

def download_model(url, dest_path):
    """Download a model file from URL."""
    print(f"Downloading {os.path.basename(dest_path)}...")
    print(f"Source: {url}")
    
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"✓ Successfully downloaded to {dest_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return False

def main():
    """Download all required models."""
    models_dir = Path(__file__).parent / "backend" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("KAAVAL Model Downloader")
    print("="*70)
    print(f"Models directory: {models_dir}\n")
    
    downloaded = 0
    failed = 0
    
    for model_name, url in MODELS.items():
        dest_path = models_dir / model_name
        
        # Check if model already exists
        if dest_path.exists():
            print(f"✓ {model_name} already exists, skipping...")
            continue
        
        # Try to download from GitHub
        if download_model(url, dest_path):
            downloaded += 1
        else:
            # If GitHub fails, try alternative source
            if model_name == "gfpgan.pth":
                print(f"  Trying alternative source for {model_name}...")
                alt_url = "https://huggingface.co/TencentARC/GFPGAN/resolve/main/GFPGANv1.4.pth"
                if download_model(alt_url, dest_path):
                    downloaded += 1
                else:
                    failed += 1
            else:
                failed += 1
    
    print("\n" + "="*70)
    print(f"Download Summary: {downloaded} successful, {failed} failed")
    print("="*70)
    
    # List all models in directory
    print("\nAvailable models in directory:")
    for model_file in sorted(models_dir.glob("*")):
        if model_file.is_file():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ {model_file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
