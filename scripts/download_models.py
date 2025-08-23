#!/usr/bin/env python3
"""
Script to pre-download required models for BookSpine KTE module.

This script downloads the required Hugging Face models to avoid rate limiting
during tests and first-time usage.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Configuration constants
DISABLE_TELEMETRY = "1"  # nosec B105 - Disable HF telemetry
DISABLE_IMPLICIT_TOKEN = "1"  # nosec B105 - Disable implicit token usage

# will load variables from .env into os.environ
load_dotenv()


def download_models():
    """Download required models for KTE functionality."""
    try:
        print("Downloading required models for BookSpine KTE...")

        # Set environment variables to reduce API calls
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = DISABLE_TELEMETRY
        os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = DISABLE_IMPLICIT_TOKEN

        # Check for Hugging Face API token
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            print("✅ Using Hugging Face API token for authentication")
            os.environ["HF_TOKEN"] = hf_token
        else:
            print("ℹ️  No HF_TOKEN found - using anonymous access (may be rate limited)")
            print("   To avoid rate limiting, set HF_TOKEN environment variable")
            print("   Get a free token at: https://huggingface.co/settings/tokens")

        # Import after setting environment variables
        from sentence_transformers import SentenceTransformer

        # Download the model
        model_name = "all-MiniLM-L6-v2"
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")

        print(f"Downloading {model_name} to {cache_dir}...")

        # This will download and cache the model
        model = SentenceTransformer(model_name, cache_folder=cache_dir, device="cpu")

        print(f"✅ Successfully downloaded and cached {model_name}")
        print(f"Model cache location: {cache_dir}")

        # Test the model
        test_text = "This is a test sentence for model verification."
        embeddings = model.encode(test_text)
        print(f"✅ Model test successful - embedding shape: {embeddings.shape}")

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please install required dependencies:")
        print("pip install sentence-transformers keybert")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error downloading models: {e}")
        if "429" in str(e) or "rate limit" in str(e).lower():
            print("\n💡 Rate limiting detected. Try:")
            print("   1. Set HF_TOKEN environment variable")
            print("   2. Wait a few minutes and try again")
            print("   3. Get a free token at: https://huggingface.co/settings/tokens")
        sys.exit(1)


if __name__ == "__main__":
    download_models()
