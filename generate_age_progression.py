#!/usr/bin/env python3
"""
Generate age progression variants from a base human face image
This script creates 8 age variants (18, 25, 35, 45, 55, 65, 75, 80) from a base image
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import sys

def generate_age_progressions(base_image_path, output_dir="frontend/sample_images"):
    """Generate 8 age progression variants from base image"""
    
    if not os.path.exists(base_image_path):
        print(f"[!] Error: Base image not found at {base_image_path}")
        return False
    
    try:
        # Load the base image
        img = Image.open(base_image_path)
        print(f"[✓] Base face image loaded: {img.size}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        ages = [18, 25, 35, 45, 55, 65, 75, 80]
        print("[*] Generating 8 age progression variants...\n")
        
        for age in ages:
            # Create a copy of the original
            variant = img.copy()
            
            # Apply age-based transformations
            if age <= 25:
                # Young: bright, clear, vibrant skin
                print(f"  Processing Age {age}: Young adult (enhanced clarity)")
                
                # Enhance color saturation
                enhancer = ImageEnhance.Color(variant)
                variant = enhancer.enhance(1.15)
                
                # Brighten slightly
                enhancer = ImageEnhance.Brightness(variant)
                variant = enhancer.enhance(1.08)
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(variant)
                variant = enhancer.enhance(1.1)
                
            elif age <= 40:
                # Middle age: balanced, slight wear
                print(f"  Processing Age {age}: Middle aged (balanced appearance)")
                
                # Slightly desaturate
                enhancer = ImageEnhance.Color(variant)
                variant = enhancer.enhance(0.95)
                
                # Reduce brightness slightly
                enhancer = ImageEnhance.Brightness(variant)
                variant = enhancer.enhance(1.0)
                
                # Add subtle texture overlay for aging
                overlay = Image.new('RGBA', variant.size, (180, 140, 120, 15))
                variant = Image.alpha_composite(variant.convert('RGBA'), overlay).convert('RGB')
                
            else:
                # Older: mature appearance, more pronounced aging
                print(f"  Processing Age {age}: Senior (mature appearance)")
                
                # Desaturate more
                enhancer = ImageEnhance.Color(variant)
                variant = enhancer.enhance(0.75)
                
                # Reduce brightness
                enhancer = ImageEnhance.Brightness(variant)
                variant = enhancer.enhance(0.92)
                
                # Reduce contrast slightly
                enhancer = ImageEnhance.Contrast(variant)
                variant = enhancer.enhance(0.95)
                
                # Add aging texture
                overlay = Image.new('RGBA', variant.size, (140, 100, 80, 50))
                variant = Image.alpha_composite(variant.convert('RGBA'), overlay).convert('RGB')
            
            # Apply subtle blur for skin smoothing
            variant = variant.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # Save the variant
            output_path = f"{output_dir}/age_progression_{age}.jpg"
            variant.save(output_path, quality=95)
            print(f"    ✓ Saved: {os.path.basename(output_path)}")
        
        print(f"\n[✓] Successfully generated all 8 age progression variants!")
        print(f"[✓] Output directory: {os.path.abspath(output_dir)}")
        return True
        
    except Exception as e:
        print(f"[!] Error processing image: {str(e)}")
        return False

if __name__ == "__main__":
    # Path to the base face image
    base_image = "frontend/sample_images/base_face.jpg"
    
    # Generate the age progressions
    success = generate_age_progressions(base_image)
    
    if not success:
        print("\n[!] Failed to generate age progressions.")
        print("[*] Please ensure 'base_face.jpg' exists in frontend/sample_images/")
        sys.exit(1)
