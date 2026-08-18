# Crew AI tutorials
> Venkata Bhattaram
> github.com/v-bhattaram

## Installation

This repo already has a working local venv (see [rag-building.md §10](rag-building.md#10-implementation--how-to-run)
for the full local Postgres/Qdrant/Ollama setup) — this section is the
minimal, standalone CrewAI install for following along with the topics below.

```
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install crewai crewai-tools
```

- Requires Python 3.10–3.13 (check with `python --version`).
- `crewai` — core framework (Agent, Task, Crew, Process, Flow).
- `crewai-tools` — optional but recommended: built-in tools (search, scrape, RAG, MCP adapter, etc.), pulled in separately so the core stays lean.
- Verify the CLI is on PATH: `.venv\Scripts\crewai --version`.
- Scaffold a fresh project (separate from this repo's existing layout) with `crewai create crew <name>` — generates `agents.yaml`, `tasks.yaml`, `crew.py`, `main.py`.
- API keys: only needed for hosted LLM providers. For the local-Ollama path this repo uses, none are required — see `common/config.py` and `common/ollama_client.py`.
- Add `crewai`/`crewai-tools` to [requirements.txt](requirements.txt) to pin versions for this project (`crewai` is already listed; add `crewai-tools` when you start using its built-in tools).

## Topics

### 1. [Foundations](topics/01-foundations.md)
- [ ] What is CrewAI vs. LangChain/LangGraph/AutoGen — when to reach for it
- [ ] Core architecture: Agents, Tasks, Crews, Process, Flows
- [ ] Project scaffolding (`crewai create crew`, folder layout, `pyproject.toml`) — see [Installation](#installation) above
- [ ] `crewai` CLI: run, train, test, replay, log-tasks-outputs
- [ ] Config-driven setup: `agents.yaml` + `tasks.yaml` vs. defining in Python

### 2. [Agents](topics/02-agents.md)
- [ ] Anatomy of an `Agent`: role, goal, backstory, and why they shape output quality
- [ ] `llm` param — wiring different providers/models per agent (incl. local via Ollama)
- [ ] `allow_delegation`, `verbose`, `max_iter`, `max_rpm`, `max_execution_time`
- [ ] `memory` and `cache` flags on an agent
- [ ] `respect_context_window` and context handling for long conversations
- [ ] Custom agent reasoning strategies (`reasoning=True`, self-reflection loop)
- [ ] Function-calling / structured output agents

### 3. [Tasks](topics/03-tasks.md)
- [ ] Anatomy of a `Task`: description, expected_output, agent, context
- [ ] Task `context` — chaining outputs from one task into another
- [ ] `output_json` / `output_pydantic` for structured, typed results
- [ ] `output_file` for persisting task results
- [ ] Synchronous vs. `async_execution=True` tasks
- [ ] Conditional tasks (`ConditionalTask`) and guardrails on outputs
- [ ] Human-in-the-loop tasks (`human_input=True`)

### 4. [Tools](topics/04-tools.md)
- [ ] Built-in tools: `crewai-tools` package (search, scrape, file, code interpreter, RAG)
- [ ] Writing custom tools with `BaseTool` / `@tool` decorator
- [ ] Tool input schemas via Pydantic
- [ ] Tool error handling & retries
- [ ] Assigning tools at agent level vs. task level
- [ ] LangChain tool interop (reusing LangChain tools inside CrewAI)
- [ ] MCP (Model Context Protocol) tool integration

### 5. [Crews & Process](topics/05-crews-process.md)
- [ ] `Process.sequential` — linear task execution
- [ ] `Process.hierarchical` — manager LLM delegates to agents
- [ ] Writing a custom manager agent for hierarchical crews
- [ ] Crew-level `memory`, `cache`, `planning`, `verbose`
- [ ] `kickoff()`, `kickoff_for_each()`, `kickoff_async()`
- [ ] Passing runtime `inputs` and templating into role/goal/description strings
- [ ] Callbacks: `step_callback`, `task_callback` for observability mid-run

### 6. [Memory & Knowledge](topics/06-memory-knowledge.md)
- [ ] Short-term memory (per-run) vs. long-term memory (across runs, SQLite-backed)
- [ ] Entity memory — tracking people/objects/concepts across a run
- [ ] Contextual memory composition (how CrewAI blends the three)
- [ ] `Knowledge` sources: strings, files, PDFs, CSV, JSON as agent-accessible knowledge
- [ ] Custom embeddings/vector DB providers for memory & knowledge (this pairs directly with the Qdrant/Postgres RAG stack in [rag-building.md](rag-building.md))
- [ ] Resetting memory between runs (`crewai reset-memories`)

### 7. [Flows (event-driven orchestration)](topics/07-flows.md)
- [ ] `Flow` vs. `Crew` — when orchestration logic needs branching/state beyond a pipeline
- [ ] `@start`, `@listen`, `@router` decorators
- [ ] Flow state management (structured state with Pydantic models)
- [ ] Combining multiple Crews inside a single Flow
- [ ] Conditional branching and `or_`/`and_` listener composition
- [ ] Persisting and resuming Flow state

### 8. [LLM Integration](topics/08-llm-integration.md)
- [ ] Provider-agnostic LLM config via `LLM` class (OpenAI, Anthropic, Ollama, Azure, Bedrock, etc.)
- [ ] Local model serving with Ollama — model selection, context length tradeoffs
- [ ] Temperature, top_p, and other generation params per agent
- [ ] Cost/token tracking per crew run
- [ ] Structured output enforcement (JSON mode / function calling) across providers

### 9. [Testing, Debugging & Observability](topics/09-testing-observability.md)
- [ ] `crewai test` — evaluating crew quality against a task/expected-output set
- [ ] `crewai replay` — replaying from a specific task to speed up iteration
- [ ] Verbose logging levels and reading agent "thought" traces
- [ ] Tracing integrations: AgentOps, Langfuse, Portkey, OpenTelemetry
- [ ] Common failure modes: infinite delegation loops, tool hallucination, context overflow

### 10. [Deployment & Production](topics/10-deployment.md)
- [ ] Packaging a crew as a service (FastAPI wrapper, CLI, or CrewAI AMP)
- [ ] Env/config management (`.env`, per-environment settings) — reuse patterns from [common/config.py](common/config.py)
- [ ] Rate limiting (`max_rpm`) and cost guardrails for production runs
- [ ] Error handling & retries around tool/LLM failures
- [ ] Scaling: running multiple crews concurrently, queueing kickoffs

### 11. [Applied Projects (build to learn)](topics/11-applied-projects.md)
- [ ] Research crew: web-search agent → summarizer agent → writer agent (sequential)
- [ ] Hierarchical crew: manager agent delegating to specialist agents
- [ ] RAG-powered crew: point an agent's tool at the existing Qdrant/Postgres RAG pipeline in this repo instead of building a new retriever
- [ ] Flow-based multi-crew pipeline with conditional routing and persisted state
- [ ] Crew with human-in-the-loop approval before a final action (e.g. sending an email, writing a file)
- [ ] Add tracing/eval to one of the above and compare before/after prompt tuning

## References
- Official docs: docs.crewai.com
- `crewai-tools` repo for the current built-in tool catalog
- [rag-building.md](rag-building.md) — this repo's own RAG notes, useful as a knowledge/tool backend for crews
