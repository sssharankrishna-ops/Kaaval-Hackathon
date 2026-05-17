#!/usr/bin/env python3
"""Test restoration pipeline with specific input/output paths."""

from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.ml.reconstruction.reconstructor import Reconstructor

def main():
    # Define paths
    input_path = Path(r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_1_damaged.jpeg")
    expected_output = Path(r"D:\KAVHACK\KAAVALFINAL-20260119T012636Z-3-001\KAAVALFINAL\kaaval dataset\person_1_reconstructed.jpeg")
    
    # Check if input exists
    if not input_path.exists():
        print(f"ERROR: Input image not found: {input_path}")
        return 1
    
    print(f"Input image: {input_path}")
    print(f"Expected output: {expected_output}")
    
    # Initialize reconstructor
    print("\nInitializing Reconstructor...")
    reconstructor = Reconstructor()
    
    if not reconstructor.available():
        print("WARNING: No reconstruction backend available!")
    
    # Run restoration
    print("\nRunning restoration...")
    try:
        output_path, confidence = reconstructor.reconstruct_from_path(input_path)
        print(f"✓ Restoration complete!")
        print(f"  Output: {output_path}")
        print(f"  Confidence: {confidence:.2%}")
        
        # Verify it matches expected output
        if output_path == expected_output:
            print(f"✓ Output path matches expected path!")
        else:
            print(f"⚠ Output path differs from expected:")
            print(f"  Expected: {expected_output}")
            print(f"  Got:      {output_path}")
        
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
