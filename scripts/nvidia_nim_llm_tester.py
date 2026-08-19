"""
Test the NVIDIA NIM cloud LLM through CrewAI's LLM class.

Usage:
    python -m scripts.nvidia_nim_llm_tester
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

PROMPT = "Reply with exactly one short sentence confirming you are working."


def test_nvidia_nim_llm() -> bool:
    """Send a test prompt to an NVIDIA NIM cloud LLM."""

    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        print("NVIDIA_API_KEY is missing from scripts/.env")
        return False

    llm = LLM(
        model="openai/meta/llama-3.1-8b-instruct",
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1",
        temperature=0.3,
    )

    print("Calling NVIDIA NIM model...")

    try:
        response = llm.call(PROMPT)
    except Exception as exc:
        print(f"NVIDIA NIM LLM call FAILED: {exc}")
        return False

    print("NVIDIA NIM LLM call succeeded.")
    print(f"  Prompt  : {PROMPT}")
    print(f"  Response: {response}")

    return True


if __name__ == "__main__":
    ok = test_nvidia_nim_llm()
    sys.exit(0 if ok else 1)