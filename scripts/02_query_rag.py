"""
Step 2 - Call the RAG index and size the tokens involved.

Embeds a query, searches the Qdrant collection built by 01_build_rag.py,
and reports exact token counts (via Ollama's own tokenizer, see
common/ollama_client.count_tokens) for:
  - the raw query
  - each retrieved chunk
  - the assembled context block that would actually be sent to the chat
    model as part of the prompt in 03_chat_with_rag.py

Usage:
    python scripts/02_query_rag.py --query "What laptops do you have in stock?"
    python scripts/02_query_rag.py --query "..." --top-k 3
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client import QdrantClient

from common import config, ollama_client


def build_context_block(hits) -> str:
    lines = []
    for hit in hits:
        lines.append(f"- {hit.payload['text']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Query the product_catalog RAG index and size the tokens involved.")
    parser.add_argument("--query", required=True, help="Natural-language question to search the index with.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    client = QdrantClient(url=config.QDRANT_URL)

    query_vector = ollama_client.embed(args.query)
    hits = client.query_points(
        collection_name=config.COLLECTION_NAME,
        query=query_vector,
        limit=args.top_k,
    ).points

    print(f"Query: {args.query!r}")
    print(f"Retrieved {len(hits)} chunk(s) from '{config.COLLECTION_NAME}':\n")
    for hit in hits:
        print(f"  score={hit.score:.4f}  product_id={hit.payload['source_pk']}  {hit.payload['product_name']}")
        print(f"    {hit.payload['text']}")
    print()

    context_block = build_context_block(hits)

    query_tokens = ollama_client.count_tokens(args.query)
    context_tokens = ollama_client.count_tokens(context_block)
    per_chunk_tokens = [ollama_client.count_tokens(hit.payload["text"]) for hit in hits]

    print(f"Token size (exact, via {config.OLLAMA_CHAT_MODEL} tokenizer):")
    print(f"  Query tokens              : {query_tokens}")
    for hit, tok in zip(hits, per_chunk_tokens):
        print(f"  Chunk tokens (product {hit.payload['source_pk']:>4}) : {tok}")
    print(f"  Assembled context tokens  : {context_tokens}")
    print(f"  Total call size (query + context) : {query_tokens + context_tokens}")


if __name__ == "__main__":
    main()
