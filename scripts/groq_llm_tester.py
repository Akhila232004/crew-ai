"""
Test the Groq cloud LLM through CrewAI's provider-agnostic LLM class.

Usage:
    python -m scripts.groq_llm_tester
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

PROMPT = "Reply with exactly one short sentence confirming you are working."


def test_groq_llm() -> bool:
    """Send a test prompt to the Groq cloud LLM."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("GROQ_API_KEY is missing from scripts/.env")
        return False

    llm = LLM(
        model="groq/openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.3,
    )

    print("Calling Groq model...")

    try:
        response = llm.call(PROMPT)
    except Exception as exc:
        print(f"Groq LLM call FAILED: {exc}")
        return False

    print("Groq LLM call succeeded.")
    print(f"  Prompt  : {PROMPT}")
    print(f"  Response: {response}")

    return True


if __name__ == "__main__":
    ok = test_groq_llm()
    sys.exit(0 if ok else 1)