# -*- coding: utf-8 -*-
"""
Download models script - use China mirror
"""
import os
import sys
from pathlib import Path

# Set China mirror
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# Model cache directory
DEFAULT_CACHE_DIR = Path(__file__).parent / 'models'
os.environ['TRANSFORMERS_CACHE'] = str(DEFAULT_CACHE_DIR)
os.environ['HF_HOME'] = str(DEFAULT_CACHE_DIR)
os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(DEFAULT_CACHE_DIR)
os.environ['HUGGINGFACE_HUB_CACHE'] = str(DEFAULT_CACHE_DIR)

def download_models():
    """Download models"""
    print("=" * 60)
    print("Starting download (using hf-mirror.com)")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer, CrossEncoder
        
        # Download Embedding model
        print("\n[1/2] Download Embedding model: BAAI/bge-small-zh")
        print("      Size: ~100MB")
        print("-" * 60)
        
        try:
            SentenceTransformer('BAAI/bge-small-zh', cache_folder=str(DEFAULT_CACHE_DIR))
            print("Embedding model downloaded")
        except Exception as e:
            print(f"Embedding model failed: {e}")
            return False
        
        # Download Reranker model
        print("\n[2/2] Download Reranker model: BAAI/bge-reranker-v2-m3")
        print("      Size: ~500MB")
        print("-" * 60)
        
        try:
            CrossEncoder('BAAI/bge-reranker-v2-m3', cache_folder=str(DEFAULT_CACHE_DIR))
            print("Reranker model downloaded")
        except Exception as e:
            print(f"Reranker model failed: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("All models downloaded!")
        print(f"Location: {DEFAULT_CACHE_DIR}")
        print("=" * 60)
        return True
        
    except ImportError:
        print("Error: Please install dependencies: pip install sentence-transformers")
        return False

def manual_instructions():
    """Manual download instructions"""
    print("""
If download stuck, try manual methods:

Method 1: Use git-lfs
---------------------
git lfs install
mkdir -p ai_module/models/BAAI
cd ai_module/models/BAAI
git clone https://hf-mirror.com/BAAI/bge-small-zh
git clone https://hf-mirror.com/BAAI/bge-reranker-v2-m3

Method 2: Use browser
---------------------
1. Visit https://hf-mirror.com/BAAI/bge-small-zh
2. Download pytorch_model.bin and config.json
3. Put in ai_module/models/BAAI/bge-small-zh/
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        manual_instructions()
    else:
        print("Tip: Run with --help for manual download instructions\n")
        
        success = download_models()
        if not success:
            manual_instructions()