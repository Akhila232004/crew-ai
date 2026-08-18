# 2. Agents

[← back to crew-ai.md](../crew-ai.md)

## Anatomy of an Agent

```python
from crewai import Agent

researcher = Agent(
    role="Senior Data Researcher",
    goal="Find accurate, up-to-date information on {topic}",
    backstory=(
        "You work at a leading tech think tank. Your expertise lies in "
        "identifying emerging trends and separating signal from hype."
    ),
    llm="ollama/llama3.2",
    tools=[...],
    verbose=True,
)
```

`role`, `goal`, and `backstory` are not metadata — they are concatenated
into the system prompt CrewAI builds for every task this agent runs.
Vague personas produce vague, generic output; specific personas produce
noticeably more focused output. This is the single highest-leverage thing
to iterate on when a crew underperforms, before reaching for bigger models
or more tools.

## `llm` — provider/model wiring

Accepts a string (`"gpt-4o"`, `"ollama/llama3.2"`, `"anthropic/claude-sonnet-4-5"`)
or a `crewai.LLM` instance for explicit control over base URL, temperature,
etc. See [08-llm-integration.md](08-llm-integration.md) for provider details.
Different agents in the same crew can use different models — e.g. a cheap/fast
model for a summarizer agent, a stronger model for the final writer agent.

## Execution-control parameters

| Param | Default | What it does |
|---|---|---|
| `allow_delegation` | `False` (v0.30+) | Lets this agent hand off sub-work to other agents via built-in delegation tools |
| `verbose` | `False` | Prints the agent's reasoning/tool-call trace |
| `max_iter` | 20 | Max reasoning/tool-call loops before forcing an answer |
| `max_rpm` | `None` | Requests-per-minute cap — throttles this agent's LLM calls |
| `max_execution_time` | `None` | Wall-clock timeout per task execution |
| `respect_context_window` | `True` | Auto-summarizes when approaching the model's context limit instead of erroring |

`max_iter` and `max_execution_time` are your main defenses against an agent
looping forever on a bad tool result — set them explicitly in production
rather than trusting defaults.

## `memory` and `cache`

- `memory=True` on an agent lets it use CrewAI's memory system (short-term,
  long-term, entity — see [06-memory-knowledge.md](06-memory-knowledge.md))
  to recall context across tasks/runs.
- `cache=True` caches tool call results so identical tool calls (same tool,
  same args) within a run aren't re-executed — useful for expensive/rate-limited
  tools like web search.

## `respect_context_window` and long conversations

When an agent's accumulated reasoning + tool outputs approach the model's
context window, CrewAI either truncates/summarizes (`respect_context_window=True`,
default) or raises an error (`False`, forces you to redesign the task to
produce less intermediate output). For local small-context models (e.g.
`llama3.2` at 8k–128k depending on config), keep this on and design tools to
return concise, structured results rather than raw dumps — this is exactly
why [02_query_rag.py](../scripts/02_query_rag.py) in this repo reports exact
token counts per retrieved chunk, so you can size `top_k` before context
becomes a problem.

## Custom reasoning strategies

`reasoning=True` makes the agent produce an explicit plan before acting
(plan → critique → refine loop) rather than jumping straight to tool calls.
Improves reliability on multi-step tasks at the cost of extra LLM calls —
worth it for agents doing non-trivial synthesis, probably overkill for a
single-tool-call lookup agent.

## Function-calling / structured output agents

Pair an agent with `output_pydantic`/`output_json` on its **Task** (not the
agent itself — see [03-tasks.md](03-tasks.md)) to force machine-parseable
output. Whether this uses native function-calling under the hood depends on
the provider; CrewAI falls back to instructed JSON output + parsing for
providers/models without native structured-output support (relevant for
smaller local Ollama models, which don't always follow schema instructions
as reliably as hosted frontier models — validate output_pydantic results in
that case rather than assuming it always parses).
