# 4. Tools

[← back to crew-ai.md](../crew-ai.md)

## Built-in tools (`crewai-tools`)

Installed separately (`pip install crewai-tools`, see
[Installation](../crew-ai.md#installation)). Notable categories:

| Category | Examples |
|---|---|
| Search/scrape | `SerperDevTool`, `WebsiteSearchTool`, `ScrapeWebsiteTool` |
| File I/O | `FileReadTool`, `DirectoryReadTool`, `FileWriterTool` |
| Code execution | `CodeInterpreterTool` (sandboxed Docker execution) |
| RAG-ish | `RagTool`, `PDFSearchTool`, `CSVSearchTool`, `PGSearchTool` |
| MCP | `MCPServerAdapter` — bridges to any MCP server's tools |

`PGSearchTool` and `RagTool` are CrewAI's convenience wrappers for
"point a tool at a data source and let it embed/search automatically." For
anything with real production requirements — deterministic point IDs,
incremental sync, blue-green reindexing, PII handling — build the pipeline
yourself, as this repo does (see [rag-building.md](../rag-building.md)), and
expose it as a **custom tool** instead. That's exactly what
[scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py) does.

## Writing custom tools

Two ways, same result:

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="The search query")
    top_k: int = Field(5, description="Number of results to return")

class ProductCatalogSearchTool(BaseTool):
    name: str = "product_catalog_search"
    description: str = "Search the product catalog by semantic similarity."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str, top_k: int = 5) -> str:
        # ... embed query, search Qdrant, return formatted string
        ...
```

```python
from crewai.tools import tool

@tool("product_catalog_search")
def product_catalog_search(query: str, top_k: int = 5) -> str:
    """Search the product catalog by semantic similarity."""
    ...
```

Use `BaseTool` when the tool needs shared state/config (e.g. a Qdrant client
initialized once), the `@tool` decorator for simple, stateless functions.
Either way, **the docstring/description is what the LLM reads to decide
when to call the tool** — write it like a function-calling spec, not
internal documentation.

## Tool input schemas via Pydantic

`args_schema` is what turns free-text LLM intent into validated, typed
arguments — the LLM's tool call is parsed against this schema before `_run`
executes. Tight schemas (explicit `Field` descriptions, sensible defaults,
enums for constrained choices) measurably reduce malformed tool calls,
especially with smaller/local models that are less reliable at
function-calling than frontier hosted models.

## Error handling & retries

A tool's `_run` should catch its own expected failure modes and **return a
descriptive string**, not raise — an uncaught exception aborts the agent's
reasoning loop, while a returned error string ("No products found matching
that query") lets the agent adapt (try a different query, ask for
clarification, etc.). Reserve raising for truly unrecoverable
infrastructure failures (e.g. the vector DB is unreachable).

## Tool assignment: agent-level vs. task-level

- Tools passed to `Agent(tools=[...])` are available for every task that
  agent runs.
- Tools passed to `Task(tools=[...])` are scoped to just that task
  (overrides/extends the agent's tools for that task only).

Prefer agent-level for tools central to the agent's whole role (e.g. the
catalog search tool for a "shopping assistant" agent); use task-level for a
one-off capability only one task needs (e.g. a "send the final email" tool
that shouldn't be available during earlier drafting tasks).

## LangChain tool interop

CrewAI can wrap a LangChain `Tool`/`BaseTool` directly — useful if you
already have a library of LangChain tools and don't want to reimplement
them. Generally prefer native CrewAI tools going forward since LangChain
is no longer a runtime dependency of CrewAI itself; interop is a migration
aid, not the recommended steady state.

## MCP tool integration

See the dedicated writeup: MCP lets an agent consume tools from an external
**Model Context Protocol** server (local via stdio, or remote via SSE /
streamable HTTP) without hand-writing a `BaseTool` for each one.

```python
from crewai_tools import MCPServerAdapter
from crewai import Agent

with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
    agent = Agent(role="...", goal="...", backstory="...", tools=mcp_tools)
```

Tool names get prefixed with the server name to avoid collisions across
multiple connected servers. Natural next step for this repo: if the
Postgres/Qdrant RAG pipeline in [rag-building.md](../rag-building.md) is
ever stood up as its own MCP server, `03_chat_with_rag.py`'s hand-written
`product_catalog_search` tool could be replaced by an `MCPServerAdapter`
connection — same agent, tool sourced externally instead of in-process.
