"""Thin wrapper around the local Ollama HTTP API for embeddings and chat."""

import requests

from . import config


def embed(text: str) -> list[float]:
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.OLLAMA_EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def count_tokens(text: str, model: str | None = None) -> int:
    """
    Exact token count for the given model's own tokenizer, fully local:
    asks Ollama to evaluate the prompt and generate just 1 token, then
    reads back prompt_eval_count. No external network calls (unlike
    tiktoken, which fetches its BPE file from openaipublic's blob storage).
    """
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model or config.OLLAMA_CHAT_MODEL,
            "prompt": text,
            "stream": False,
            "options": {"num_predict": 1},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["prompt_eval_count"]


def chat(messages: list[dict], model: str | None = None) -> dict:
    """Non-streaming chat call. Returns {"content", "prompt_tokens", "completion_tokens"}."""
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/chat",
        json={"model": model or config.OLLAMA_CHAT_MODEL, "messages": messages, "stream": False},
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "content": data["message"]["content"],
        # Ollama reports the model's own tokenizer counts for the actual call made.
        "prompt_tokens": data.get("prompt_eval_count"),
        "completion_tokens": data.get("eval_count"),
    }
