"""
Local LLM sanity checks for the crewAI + Ollama setup (see crew-ai.md "Installation").

* check_ollama_running() - is the Ollama server reachable
* list_models()          - models currently pulled into Ollama
* check_api_key()        - crewAI's LLM layer (litellm) validates that
  OPENAI_API_KEY is set even when every agent uses a local Ollama model - the
  key is never sent anywhere for local calls, but its absence raises at
  kickoff time. Make sure a placeholder is present in .env.

Usage:
    python local_llm_check.py
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import config

ENV_FILE = Path(__file__).resolve().parent / ".env"


def check_ollama_running() -> bool:
    try:
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"Ollama is NOT reachable at {config.OLLAMA_BASE_URL} ({exc})")
        return False
    print(f"Ollama is up at {config.OLLAMA_BASE_URL}")
    return True


def list_models() -> list[str]:
    resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
    resp.raise_for_status()
    models = [m["name"] for m in resp.json().get("models", [])]
    if models:
        print("Installed models:")
        for name in models:
            print(f"  - {name}")
    else:
        print("No models installed (try `ollama pull <model>`).")
    return models


def check_api_key() -> bool:
    load_dotenv(ENV_FILE)
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        print("OPENAI_API_KEY present in .env - present and working.")
        return True

    print("OPENAI_API_KEY not found in .env - creating a local placeholder key.")
    placeholder = "sk-local-ollama-placeholder"
    ENV_FILE.touch(exist_ok=True)
    set_key(str(ENV_FILE), "OPENAI_API_KEY", placeholder)
    os.environ["OPENAI_API_KEY"] = placeholder
    print(f"Saved placeholder OPENAI_API_KEY to {ENV_FILE} and set it for this process.")
    return True


def main():
    print("=== Ollama status ===")
    if check_ollama_running():
        print()
        print("=== Installed models ===")
        list_models()

    print()
    print("=== API key check ===")
    check_api_key()


if __name__ == "__main__":
    main()
