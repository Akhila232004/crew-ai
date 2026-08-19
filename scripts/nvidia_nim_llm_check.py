"""
NVIDIA NIM Cloud LLM sanity checks for the CrewAI setup.

* check_api_key() - verifies that NVIDIA_API_KEY is available
  in scripts/.env

Usage:
    python -m scripts.nvidia_nim_llm_check
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent / ".env"


def check_api_key() -> bool:
    """Check whether NVIDIA_API_KEY is present without exposing it."""

    load_dotenv(ENV_FILE)

    api_key = os.environ.get("NVIDIA_API_KEY")

    if api_key:
        print("NVIDIA_API_KEY present in .env - ready to use.")
        return True

    print("NVIDIA_API_KEY not found in .env.")
    print(f"Add NVIDIA_API_KEY to: {ENV_FILE}")
    return False


def main():
    print("=== NVIDIA NIM API Key Check ===")

    ok = check_api_key()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()