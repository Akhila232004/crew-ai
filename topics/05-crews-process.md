# 5. Crews & Process

[← back to crew-ai.md](../crew-ai.md)

## `Process.sequential`

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)
result = crew.kickoff(inputs={"topic": "local LLM serving"})
```

Tasks run in the order listed; each task automatically has access to the
outputs of tasks before it. This is the default and the right starting
point for any linear pipeline (research → draft → edit, extract → transform
→ report, etc.).

## `Process.hierarchical`

A **manager LLM** (either an auto-generated manager, or one you supply via
`manager_agent=`/`manager_llm=`) plans the work, decides which agent handles
which task, and can re-delegate — closer to how a real team lead operates,
at the cost of an extra planning LLM call and less predictable execution
order.

```python
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[...],
    process=Process.hierarchical,
    manager_llm="gpt-4o",   # the manager needs a capable model to plan well
)
```

Use hierarchical when task-to-agent assignment genuinely depends on runtime
context (which you can't know ahead of time), not just because it "sounds
more agentic" — sequential is easier to debug and reason about, and should
be the default unless delegation logic is actually dynamic.

## Custom manager agent

Instead of an auto-generated manager, supply your own `Agent` as
`manager_agent=` with a tailored role/goal/backstory for planning and
delegation quality — worth doing once the default manager's delegation
choices are visibly suboptimal (e.g. always picking the same agent
regardless of task fit).

## Crew-level settings

| Param | Purpose |
|---|---|
| `memory=True` | Enables the crew-wide memory system (short/long-term/entity) |
| `cache=True` | Caches tool results across the crew run |
| `planning=True` | Runs an upfront planning LLM call that produces a step-by-step plan before task execution begins — improves task ordering/quality on complex crews at the cost of one extra LLM call |
| `verbose=True` | Prints full execution trace |

## Kickoff variants

| Method | Use when |
|---|---|
| `kickoff(inputs={...})` | Single run, synchronous |
| `kickoff_for_each(inputs=[{...}, {...}])` | Run the same crew once per input dict — batch processing |
| `kickoff_async(inputs={...})` | Non-blocking, `await`-able — for integrating into an async app (e.g. FastAPI endpoint) |

## Runtime inputs and templating

Any `{variable}` in `role`/`goal`/`backstory`/`description`/`expected_output`
is filled from the `inputs` dict passed to `kickoff()`. This is what makes a
single crew definition reusable across many invocations instead of hardcoding
values — e.g. `{topic}` in [01-foundations.md](01-foundations.md)'s YAML
example gets filled per-run rather than requiring a new Agent per topic.

## Callbacks

- `step_callback=fn` — fires after each individual agent step (thought/tool
  call/observation) — use for live progress UI or fine-grained logging.
- `task_callback=fn` — fires after each task completes — use for
  checkpointing intermediate results (e.g. writing each task's output to a
  DB row as it finishes, rather than waiting for the whole crew to finish).

Both are the hook points for wiring in custom observability without a full
tracing integration (see [09-testing-observability.md](09-testing-observability.md)).
