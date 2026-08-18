"""
Cheap, fully-offline token estimate (chars/4 heuristic) for informational
summaries where an exact count isn't worth a model call.

For the *exact* token count of a specific call (what actually gets sent to
the model), use ollama_client.count_tokens() instead — it reads Ollama's
own tokenizer output via prompt_eval_count.
"""


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)
