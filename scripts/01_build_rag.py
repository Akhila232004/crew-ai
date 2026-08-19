"""
Step 1 - RAG creation.

Full backfill (README.md section 2): reads the current product catalog out
of PostgreSQL, builds one denormalized document per product, embeds each
with a local Ollama embedding model, and upserts into a Qdrant collection
using deterministic point IDs (README.md section 5).

Usage:
    python scripts/01_build_rag.py                 # create collection if missing, upsert all products
    python scripts/01_build_rag.py --recreate       # drop and recreate the collection first
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from common import config, ollama_client, postgres_docs, tokens


def ensure_collection(client: QdrantClient, recreate: bool):
    exists = client.collection_exists(config.COLLECTION_NAME)
    if exists and recreate:
        client.delete_collection(config.COLLECTION_NAME)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=VectorParams(size=config.EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"Created collection '{config.COLLECTION_NAME}' (dim={config.EMBED_DIM}, cosine).")
    else:
        print(f"Using existing collection '{config.COLLECTION_NAME}'.")


def main():
    parser = argparse.ArgumentParser(description="Build/refresh the product_catalog RAG index in Qdrant.")
    parser.add_argument("--recreate", action="store_true", help="Drop and recreate the collection first.")
    args = parser.parse_args()

    print(f"Fetching product documents from Postgres ({config.POSTGRES['dbname']}@{config.POSTGRES['host']})...")
    conn = postgres_docs.connect()
    try:
        docs = postgres_docs.fetch_product_documents(conn)
    finally:
        conn.close()
    print(f"Built {len(docs)} product documents.")

    client = QdrantClient(url=config.QDRANT_URL)
    ensure_collection(client, args.recreate)

    total_tokens = 0
    points = []
    start = time.time()
    for i, doc in enumerate(docs, 1):
        vector = ollama_client.embed(doc["text"])
        total_tokens += tokens.estimate_tokens(doc["text"])
        points.append(PointStruct(id=doc["point_id"], vector=vector, payload=doc["payload"]))
        print(f"  [{i}/{len(docs)}] embedded product_id={doc['payload']['source_pk']}")

    client.upsert(collection_name=config.COLLECTION_NAME, points=points)
    elapsed = time.time() - start

    count = client.count(config.COLLECTION_NAME, exact=True).count
    print()
    print("Done.")
    print(f"  Points upserted this run : {len(points)}")
    print(f"  Total points in collection: {count}")
    print(f"  Approx. tokens embedded  : {total_tokens}")
    print(f"  Elapsed                  : {elapsed:.1f}s")


if __name__ == "__main__":
    main()
