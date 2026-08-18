# 6. Memory & Knowledge

[← back to crew-ai.md](../crew-ai.md)

CrewAI distinguishes **memory** (what an agent remembers about its own
execution) from **knowledge** (external reference material you hand an
agent). Both can be backed by embeddings, but they solve different problems
— don't reach for memory when what you actually want is knowledge, or
vice versa.

## Memory types

| Type | Scope | Backing store | Purpose |
|---|---|---|---|
| Short-term | Current run only | In-memory / ChromaDB (ephemeral) | Recall earlier steps within this one `kickoff()` |
| Long-term | Across runs | SQLite (`crewai reset-memories` clears it) | Learn from past runs — e.g. "last time this task failed this way" |
| Entity | Across a run (and optionally persisted) | Vector store | Track specific people/objects/concepts mentioned, so later tasks reference the same entity consistently |
| Contextual | Composed automatically | — | CrewAI blends short-term + long-term + entity into the prompt context automatically when `memory=True` |

Enable with `Crew(memory=True)` (crew-wide) and/or `Agent(memory=True)`
(per-agent). Reset with `crewai reset-memories` — do this between
unrelated projects/experiments sharing the same working directory, or
long-term memory from an old experiment will bleed into new runs.

## Knowledge

```python
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

knowledge = StringKnowledgeSource(content="Our return policy is 30 days...")

agent = Agent(..., knowledge_sources=[knowledge])
```

Knowledge sources (`StringKnowledgeSource`, file/PDF/CSV/JSON sources) are
embedded and made retrievable to the agent automatically — CrewAI handles
the chunk/embed/retrieve loop internally, which is convenient for static
reference documents but gives you none of the control this repo's own RAG
pipeline has (deterministic IDs, incremental sync, blue-green reindex — see
[rag-building.md](../rag-building.md)).

**Rule of thumb**: use `Knowledge` for small, static, low-stakes reference
material (a policy doc, a style guide). Use a **custom tool** backed by your
own retrieval pipeline (as in
[scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py)) for anything
large, changing, or requiring the production-grade guarantees this repo's
RAG design calls out — deterministic point IDs, PII handling, drift
detection.

## Custom embeddings / vector DB providers

Both memory and knowledge accept a custom `embedder` config (provider +
model), so you can point CrewAI's own memory/knowledge subsystems at the
same local Ollama embedding model
([common/ollama_client.py](../common/ollama_client.py) already wraps this)
instead of defaulting to OpenAI embeddings — required for staying fully
local/offline, which is this repo's whole point.

```python
crew = Crew(
    ...,
    memory=True,
    embedder={
        "provider": "ollama",
        "config": {"model": "nomic-embed-text"},
    },
)
```

## Resetting memory

```
crewai reset-memories             # everything
crewai reset-memories --long      # just long-term
crewai reset-memories --entities  # just entity memory
```

Do this whenever you change the embedding model — stale vectors from a
different model are silently meaningless once the model changes (see the
blue-green collection guidance in
[rag-building.md §5](../rag-building.md#5-qdrant-collection-design), which
applies to CrewAI's own memory stores just as much as to a hand-built
Qdrant collection).
