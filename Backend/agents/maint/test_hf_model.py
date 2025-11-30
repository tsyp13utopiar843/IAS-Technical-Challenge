"""
Quick test script to verify Hugging Face model loading

Run this to test if the HF integration is working:
    python test_hf_model.py
"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("Hugging Face Model Configuration Test")
print("=" * 60)

# Check HF_MODEL_REPO
hf_repo = os.getenv('HF_MODEL_REPO')
if hf_repo:
    print(f"✓ HF_MODEL_REPO found: {hf_repo}")
else:
    print("✗ HF_MODEL_REPO not set in environment")
    print("  Set it with: export HF_MODEL_REPO=your-username/repo")

# Check huggingface_hub installation
try:
    from huggingface_hub import hf_hub_download
    print("✓ huggingface_hub is installed")
    
    if hf_repo:
        print(f"\nTesting download from: {hf_repo}")
        try:
            # Try to download model.pkl
            model_file = hf_hub_download(
                repo_id=hf_repo,
                filename="model.pkl",
                cache_dir="./.hf_cache"
            )
            print(f"✓ Successfully downloaded model.pkl")
            print(f"  Cached at: {model_file}")
            
            # Check file size
            import os
            size_mb = os.path.getsize(model_file) / (1024 * 1024)
            print(f"  File size: {size_mb:.2f} MB")
            
        except Exception as e:
            print(f"✗ Failed to download from HF: {e}")
            print(f"  Make sure the repository exists and contains model.pkl")
            
except ImportError:
    print("✗ huggingface_hub not installed")
    print("  Install it with: pip install huggingface_hub")

print("\n" + "=" * 60)
print("If all checks passed, the PM agent should load the HF model!")
print("=" * 60)
