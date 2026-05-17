import sys
import os
import torch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def log(msg):
    # Safe printing for Windows redirection
    print(msg.encode('ascii', 'ignore').decode('ascii'))

try:
    from app.ml.registry import get_registry
    from app.core.config import settings
    
    log(f"PyTorch version: {torch.__version__}")
    log(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log(f"GPU device: {torch.cuda.get_device_name(0)}")
        log(f"Capability: {torch.cuda.get_device_capability(0)}")

    log("\nInitialising ML Registry...")
    registry = get_registry(enable_age_progression=True)
    
    if registry.restorer:
        log("OK: GFPGAN Restorer loaded")
        if registry.restorer._restorer:
            if hasattr(registry.restorer._restorer, 'gfpgan'):
                device = next(registry.restorer._restorer.gfpgan.parameters()).device
                log(f"GFPGAN device: {device}")
            else:
                log("GFPGANer loaded but .gfpgan not found")
        else:
            log("FAIL: GFPGANer instance is None")
    else:
        log("FAIL: GFPGAN Restorer failed to load")

    if registry.age_progressor:
         log("OK: Age Progressor loaded")
         if hasattr(registry.age_progressor, '_net'):
             device = next(registry.age_progressor._net.parameters()).device
             log(f"StyleGAN device: {device}")
    
    log("\nVerification Complete.")

except Exception as e:
    log(f"FAIL: Verification failed with error: {e}")
