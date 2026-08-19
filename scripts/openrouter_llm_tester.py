"""
Test the OpenRouter cloud LLM through CrewAI's provider-agnostic LLM class.

Usage:
    python -m scripts.openrouter_llm_tester
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

PROMPT = "Reply with exactly one short sentence confirming you are working."


def test_openrouter_llm() -> bool:
    """Send a test prompt to an OpenRouter cloud LLM."""

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("OPENROUTER_API_KEY is missing from scripts/.env")
        return False

    llm = LLM(
        model="openrouter/openrouter/free",
        api_key=api_key,
        temperature=0.3,
    )

    print("Calling OpenRouter model...")

    try:
        response = llm.call(PROMPT)
    except Exception as exc:
        print(f"OpenRouter LLM call FAILED: {exc}")
        return False

    print("OpenRouter LLM call succeeded.")
    print(f"  Prompt  : {PROMPT}")
    print(f"  Response: {response}")

    return True


if __name__ == "__main__":
    ok = test_openrouter_llm()
    sys.exit(0 if ok else 1)