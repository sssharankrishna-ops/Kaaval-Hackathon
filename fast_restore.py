#!/usr/bin/env python3
"""Fast image restoration using GFPGAN"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def restore_image(input_path, output_path):
    """Restore a damaged image using GFPGAN"""
    try:
        print(f"[*] Loading image from: {input_path}")
        img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        
        if img is None:
            print(f"[!] Failed to load image from {input_path}")
            return False
        
        print(f"[*] Image loaded: {img.shape}")
        
        # Try to load GFPGAN
        try:
            from gfpgan import GFPGANer
            
            # Model path
            model_path = Path(__file__).parent / 'backend' / 'archive' / 'GFPGANv1.4.pth'
            if not model_path.exists():
                print(f"[!] Model not found at {model_path}")
                # Fallback: Use simple enhancement
                print("[*] Applying fallback enhancement (upscale + denoise)")
                restored = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_CUBIC)
                restored = cv2.bilateralFilter(restored, 9, 75, 75)
                restored = cv2.GaussianBlur(restored, (5, 5), 0)
                restored = cv2.addWeighted(restored, 1.2, cv2.GaussianBlur(restored, (3, 3), 0), -0.2, 0)
            else:
                print(f"[*] Loading GFPGAN model from {model_path}")
                restorer = GFPGANer(
                    scale=2,
                    model_path=str(model_path),
                    upscale=2,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=None,
                    device='cpu'
                )
                
                print("[*] Running GFPGAN restoration...")
                _, _, restored = restorer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
                print("[*] GFPGAN restoration complete")
        
        except Exception as e:
            print(f"[!] GFPGAN error: {e}")
            print("[*] Applying fallback enhancement (upscale + denoise)")
            # Simple upscaling + denoising fallback
            restored = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_CUBIC)
            restored = cv2.bilateralFilter(restored, 9, 75, 75)
            restored = cv2.GaussianBlur(restored, (5, 5), 0)
            restored = cv2.addWeighted(restored, 1.2, cv2.GaussianBlur(restored, (3, 3), 0), -0.2, 0)
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save restored image
        print(f"[*] Saving restored image to: {output_path}")
        success = cv2.imwrite(str(output_path), restored)
        
        if success:
            print(f"[✓] Restoration complete! Output saved to {output_path}")
            return True
        else:
            print(f"[!] Failed to save image to {output_path}")
            return False
            
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    input_img = r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_2_damaged.jpeg"
    output_img = r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_2_reconstructed.jpeg"
    
    print("=" * 60)
    print("KAAVAL - Image Restoration Module")
    print("=" * 60)
    
    success = restore_image(input_img, output_img)
    sys.exit(0 if success else 1)
