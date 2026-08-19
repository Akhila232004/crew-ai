"""
Shared connection settings for the RAG-over-RDBMS pipeline (see ../README.md).

Reads the same .env used by the rest of the venkatab-ai stack so this project
doesn't duplicate credentials.
"""

import os

from dotenv import load_dotenv

ENV_FILE = r"D:\GIT-CODE\git_venkata\venkatab-ai-setup\.env"
load_dotenv(ENV_FILE)

# This pipeline is fully local (Postgres + Qdrant + Ollama, all on localhost).
# CrewAI's telemetry/tracing phones home over HTTPS and just times out here,
# so turn it off before crewai is ever imported.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

# PostgreSQL (source of truth)
POSTGRES = {
    "host": "localhost",
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "user": os.environ.get("POSTGRES_USER", "ai_admin"),
    "password": os.environ.get("POSTGRES_PASSWORD", "ai_admin_pw"),
    "dbname": os.environ.get("POSTGRES_DB", "ai_setup"),
}

# Qdrant (vector store)
QDRANT_URL = f"http://localhost:{os.environ.get('QDRANT_HTTP_PORT', '6333')}"
COLLECTION_NAME = "product_catalog"

# Ollama (local embeddings + chat, per README section "using my ollama")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "llama3.2")
EMBED_DIM = 768  # nomic-embed-text output size
