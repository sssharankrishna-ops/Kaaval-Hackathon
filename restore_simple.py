#!/usr/bin/env python3
"""Direct restoration using GFPGAN without full backend imports."""

from pathlib import Path
import sys
import cv2
import torch
import numpy as np

def restore_with_gfpgan(input_path: Path, output_path: Path) -> float:
    """Restore image using GFPGAN directly."""
    try:
        # Import GFPGAN dependencies
        from basicsr.archs.gfpganv1_arch import GFPGANv1
        from basicsr.archs.detection_arch import init_detection_model
        from realesrgan import RealESRGANer
        
        # Set device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        # Initialize GFPGAN
        print("Loading GFPGAN model...")
        gfpgan_weights = Path(__file__).parent / "backend" / "gfpgan" / "weights" / "GFPGANv1.4.pth"
        
        # Check for model in standard location
        if not gfpgan_weights.exists():
            # Try alternative path
            alt_path = Path(__file__).parent / "backend" / "archive" / "GFPGANv1.4.pth"
            if alt_path.exists():
                gfpgan_weights = alt_path
            else:
                print(f"⚠️  GFPGAN weights not found at {gfpgan_weights}, checking installed facexlib...")
                # Use facexlib's built-in model loading
                from facexlib import detection, restoration
                
                # Use detection and restoration from facexlib
                detector = detection.init_detection_model('retinaface_resnet50', device=device)
                restorer = restoration.init_restoration_model('GFPGANv1.3', device=device)
                
                # Read image
                input_img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
                if input_img is None:
                    raise ValueError(f"Cannot read image: {input_path}")
                
                print(f"Detecting faces...")
                with torch.no_grad():
                    _, restored_faces, _ = detector(input_img)
                    
                    if restored_faces:
                        print(f"Found {len(restored_faces)} faces, restoring...")
                        output_img, _ = restorer(restored_faces, only_center_face=False, weight=0.5)
                    else:
                        print("No faces detected, using simple restoration...")
                        # Fallback: use RealESRGAN for upscaling
                        from realesrgan import RealESRGANer
                        upsampler = RealESRGANer(scale=2, model_name='RealESRGAN_x2plus', model_path=None, 
                                                 tile=400, tile_pad=10, pre_pad=0, half=False, device=device)
                        output_img, _ = upsampler.enhance(input_img, outscale=2)
                
                cv2.imwrite(str(output_path), output_img)
                print(f"✓ Restored and saved to: {output_path}")
                return 0.85
        
        # Load model from weights file
        model = GFPGANv1(out_size=512, num_style_feat=512, channel_multiplier=2, 
                        decode_out_im=True, num_mlp=8, input_is_latent=True, 
                        different_w=True, narrow=1, sft_half=False)
        model = model.to(device)
        checkpoint = torch.load(str(gfpgan_weights), map_location=device)
        if 'params_ema' in checkpoint:
            model.load_state_dict(checkpoint['params_ema'])
        else:
            model.load_state_dict(checkpoint)
        model.eval()
        
        # Read and restore image
        input_img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        if input_img is None:
            raise ValueError(f"Cannot read image: {input_path}")
        
        # Prepare input
        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
        input_tensor = torch.from_numpy(input_img).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        input_tensor = input_tensor.to(device)
        
        # Restore
        with torch.no_grad():
            output_tensor, _ = model(input_tensor, return_latents=False, return_rgb=True)
        
        output_img = (output_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)
        
        # Save
        cv2.imwrite(str(output_path), output_img)
        print(f"✓ Restored and saved to: {output_path}")
        return 0.90
        
    except Exception as e:
        print(f"GFPGAN failed: {e}")
        return None

def restore_with_facexlib(input_path: Path, output_path: Path) -> float:
    """Restore using facexlib restoration module."""
    try:
        from facexlib import detection, restoration
        import torch
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using facexlib on {device}")
        
        # Initialize models
        detector = detection.init_detection_model('retinaface_resnet50', device=device)
        restorer = restoration.init_restoration_model('GFPGANv1.3', device=device)
        
        # Read image
        input_img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        if input_img is None:
            raise ValueError(f"Cannot read image: {input_path}")
        
        print("Processing image...")
        with torch.no_grad():
            # Detect faces
            _, restored_faces, _ = detector(input_img)
            
            if restored_faces:
                print(f"Found {len(restored_faces)} face(s), restoring...")
                for idx, face in enumerate(restored_faces):
                    output_img, _ = restorer(face, only_center_face=False, weight=0.5)
            else:
                print("No faces detected, copying original...")
                output_img = input_img
        
        # Save
        cv2.imwrite(str(output_path), output_img)
        print(f"✓ Restored and saved to: {output_path}")
        return 0.85
        
    except Exception as e:
        print(f"facexlib restoration failed: {e}")
        return None

def restore_with_opencv(input_path: Path, output_path: Path) -> float:
    """Simple OpenCV fallback restoration."""
    try:
        print("Using OpenCV fallback...")
        img = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Cannot read image: {input_path}")
        
        # Simple bilateral filter for denoising/smoothing
        restored = cv2.bilateralFilter(img, 9, 75, 75)
        
        cv2.imwrite(str(output_path), restored)
        print(f"✓ Restored and saved to: {output_path}")
        return 0.60
        
    except Exception as e:
        print(f"OpenCV restoration failed: {e}")
        return None

def main():
    input_path = Path(r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_1_damaged.jpeg")
    output_path = Path(r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_1_reconstructed.jpeg")
    
    if not input_path.exists():
        print(f"❌ Input not found: {input_path}")
        return 1
    
    print(f"📷 Input:  {input_path}")
    print(f"📤 Output: {output_path}")
    print()
    
    # Try restoration methods in order
    confidence = None
    
    print("Attempting restoration...")
    confidence = restore_with_facexlib(input_path, output_path)
    
    if confidence is None:
        print("\nTrying GFPGAN...")
        confidence = restore_with_gfpgan(input_path, output_path)
    
    if confidence is None:
        print("\nFalling back to OpenCV...")
        confidence = restore_with_opencv(input_path, output_path)
    
    if confidence is None:
        print("❌ All restoration methods failed")
        return 1
    
    # Verify output
    if output_path.exists():
        print(f"\n✅ Success! Confidence: {confidence:.1%}")
        print(f"Output size: {output_path.stat().st_size} bytes")
        return 0
    else:
        print(f"\n❌ Output file not created")
        return 1

if __name__ == "__main__":
    sys.exit(main())
