# 9. Testing, Debugging & Observability

[← back to crew-ai.md](../crew-ai.md)

## `crewai test`

```
crewai test -n 3 --model gpt-4o
```

Runs the crew `n` times against its defined tasks and has a grading model
score each run's output quality — useful for catching regressions when you
change agent prompts, tool implementations, or swap models, without manually
eyeballing every run. Requires a scaffolded project (`agents.yaml`/`tasks.yaml`);
for a hand-written Python crew like this repo's, the equivalent is writing
your own small eval script that runs `kickoff()` N times and checks outputs
against expected criteria.

## `crewai replay`

```
crewai replay -t <task_id>
```

Re-executes from a specific task onward, reusing cached outputs for
everything before it — dramatically speeds up iterating on a later task
(e.g. tuning the writer agent) without re-running an expensive earlier task
(e.g. a slow research/search step) every time. Task IDs come from
`crewai log-tasks-outputs` or the verbose run trace.

## Verbose logging

`verbose=True` at the `Agent` and/or `Crew` level prints the full
thought → tool call → observation trace for every step. This is the first
thing to turn on when a crew produces a wrong/weird answer — it shows
exactly what the agent "saw" that led to the bad output, which is almost
always more informative than staring at the final result alone.
[scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py) already
enables this for the RAG-backed agent in this repo.

## Tracing integrations

| Tool | What it adds |
|---|---|
| AgentOps | Session replay, cost tracking, agent-specific dashboards |
| Langfuse | LLM observability — traces, prompt versioning, evals |
| Portkey | Gateway + observability, provider fallback/routing |
| OpenTelemetry | Vendor-neutral traces, exportable to any OTel backend |

CrewAI has built-in anonymous telemetry that phones home by default — this
repo explicitly disables it (`CREWAI_DISABLE_TELEMETRY=true`,
`OTEL_SDK_DISABLED=true` in [common/config.py](../common/config.py),
imported before `crewai`) to stay fully offline. If you add a tracing
integration later, that's the opt-in replacement for the telemetry you're
currently disabling — not something layered on top of it.

## Common failure modes

- **Infinite delegation loops** (hierarchical process): manager keeps
  re-delegating without converging. Mitigate with `max_iter` on agents and
  a well-scoped manager goal that includes an explicit "stop when..."
  condition.
- **Tool hallucination**: agent claims to have called a tool / cites results
  it never retrieved. Usually a sign the tool description is ambiguous
  about *when* to call it, or the agent's goal doesn't make tool use feel
  necessary — tighten both before adding more instructions to the prompt.
- **Context overflow**: silently truncated context on local/smaller-context
  models. Catch this by watching token usage (see
  [08-llm-integration.md](08-llm-integration.md)) rather than after the
  fact, when the output just looks subtly wrong.
- **Malformed structured output**: `output_pydantic` parse failures on
  models without reliable native structured output — add a `guardrail`
  (see [03-tasks.md](03-tasks.md)) that validates and triggers a retry with
  feedback instead of letting a bad parse propagate downstream.
