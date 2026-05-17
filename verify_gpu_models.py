import sys
import os
import torch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app.ml.registry import get_registry
    from app.core.config import settings
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print(f"Capability: {torch.cuda.get_device_capability(0)}")

    print("\nInitialising ML Registry...")
    # Explicitly enable things to force load
    registry = get_registry(enable_age_progression=True)
    
    if registry.restorer:
        print("✅ GFPGAN Restorer loaded")
        if registry.restorer._restorer:
            # Check the device of a parameter if possible
            # GFPGANer stores the model in .gfpgan
            if hasattr(registry.restorer._restorer, 'gfpgan'):
                device = next(registry.restorer._restorer.gfpgan.parameters()).device
                print(f"GFPGAN device: {device}")
            else:
                print("GFPGANer loaded but .gfpgan not found (might be normal for certain versions)")
        else:
            print("❌ GFPGANer instance is None")
    else:
        print("❌ GFPGAN Restorer failed to load")
        if "restorer" in registry.errors:
            print(f"Error: {registry.errors['restorer']}")

    if registry.age_progressor:
         print("✅ Age Progressor loaded")
         # StyleGAN also uses torch
         if hasattr(registry.age_progressor, '_net'):
             device = next(registry.age_progressor._net.parameters()).device
             print(f"StyleGAN device: {device}")
    
    print("\nVerification Complete.")

except Exception as e:
    print(f"❌ Verification failed with error: {e}")
    import traceback
    traceback.print_exc()
