# 8. LLM Integration

[← back to crew-ai.md](../crew-ai.md)

## Provider-agnostic LLM config

CrewAI's `LLM` class wraps LiteLLM under the hood, so any LiteLLM-supported
provider works with the same interface:

```python
from crewai import LLM

llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434",
    temperature=0.3,
)

agent = Agent(..., llm=llm)
```

| Provider | Model string example |
|---|---|
| OpenAI | `"gpt-4o"` |
| Anthropic | `"anthropic/claude-sonnet-4-5"` |
| Ollama (local) | `"ollama/llama3.2"` |
| Azure OpenAI | `"azure/<deployment-name>"` |
| AWS Bedrock | `"bedrock/anthropic.claude-..."` |

You can also just pass the model string directly to `Agent(llm=...)`
instead of building an `LLM` instance — use the full `LLM(...)` object when
you need to set `base_url`, custom headers, or per-agent generation params
beyond the default.

## Local model serving with Ollama

This repo's whole stack runs this way — see
[common/ollama_client.py](../common/ollama_client.py) and
[rag-building.md §10](../rag-building.md#10-implementation--how-to-run).
Key tradeoffs vs. hosted models:

- **Context length**: local models are often configured with a smaller
  effective context window than their hosted counterparts unless you
  explicitly raise Ollama's `num_ctx`. This directly affects how many RAG
  chunks/tool results you can pack into a prompt — see
  [02_query_rag.py](../scripts/02_query_rag.py)'s exact token reporting,
  which exists precisely to make this tradeoff visible before it causes a
  silent truncation.
- **Function-calling reliability**: smaller local models follow tool-call
  and structured-output instructions less reliably than frontier hosted
  models — tighten tool `args_schema` descriptions and validate
  `output_pydantic` results rather than assuming they always parse (see
  [02-agents.md](02-agents.md)).
- **No API keys / cost** — fully offline, no per-token billing, which is
  why this repo defaults to it.

## Generation params per agent

`temperature`, `top_p`, `max_tokens`, `stop`, etc. are set on the `LLM`
instance passed to an agent — different agents in the same crew can use
different settings (e.g. `temperature=0` for an extraction/classification
agent that needs determinism, `temperature=0.7` for a creative-writing
agent).

## Cost / token tracking

`CrewOutput.token_usage` (returned from `kickoff()`) reports
`prompt_tokens` / `completion_tokens` / `total_tokens` aggregated across
the whole run — [scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py)
already prints this. For hosted providers, multiply by that provider's
per-token pricing to get a per-run cost estimate; for local Ollama runs
there's no dollar cost, but the same numbers are still useful for context
budgeting and latency estimation.

## Structured output enforcement across providers

`Task(output_pydantic=...)` behaves differently depending on the underlying
provider's native support for structured output / function calling:
frontier hosted models (OpenAI, Anthropic) generally honor the schema
reliably via native tool-calling; models without native structured-output
support fall back to CrewAI instructing the model in-prompt to emit JSON
matching the schema, then parsing it — less reliable, worth wrapping in a
retry/guardrail (see `guardrail` in [03-tasks.md](03-tasks.md)) when using
smaller local models.
