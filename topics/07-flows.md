# 7. Flows (event-driven orchestration)

[← back to crew-ai.md](../crew-ai.md)

## `Flow` vs. `Crew`

A `Crew` is a pipeline (or manager-delegated set) of tasks. A `Flow` is a
step graph with explicit **events, branching, and shared state** — reach
for it when the orchestration logic itself (not just individual task
content) needs conditionals, loops, or multiple crews wired together.

Think of `Crew` as "one team executing a plan" and `Flow` as "the
process that decides which team runs when."

## `@start`, `@listen`, `@router`

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class MyState(BaseModel):
    topic: str = ""
    is_urgent: bool = False

class MyFlow(Flow[MyState]):
    @start()
    def classify(self):
        self.state.is_urgent = "urgent" in self.state.topic.lower()

    @router(classify)
    def route(self):
        return "urgent_path" if self.state.is_urgent else "normal_path"

    @listen("urgent_path")
    def handle_urgent(self):
        ...

    @listen("normal_path")
    def handle_normal(self):
        ...
```

- `@start()` marks entry point(s) — a flow can have multiple.
- `@listen(step)` runs after the named step (or event) completes.
- `@router(step)` runs after a step and returns a string that determines
  which `@listen`-tagged branch fires next — this is the conditional-branch
  primitive.

## State management

`Flow[StateModel]` gives every step access to `self.state`, a Pydantic
model shared across the whole flow run. Prefer a typed Pydantic state model
over a raw dict — it documents what the flow actually tracks and catches
typos/shape drift at development time rather than at runtime deep in a
step.

## Combining multiple Crews inside a Flow

```python
class ContentFlow(Flow[ContentState]):
    @start()
    def research(self):
        result = research_crew.kickoff(inputs={"topic": self.state.topic})
        self.state.research_notes = result.raw

    @listen(research)
    def write(self):
        result = writing_crew.kickoff(inputs={"notes": self.state.research_notes})
        self.state.draft = result.raw
```

This is the pattern for anything too complex for one Crew's `Process` to
express cleanly — e.g. a research Crew whose output conditionally triggers
either a "quick summary" Crew or a "deep-dive report" Crew depending on
what was found.

## Conditional branching: `or_` / `and_`

```python
from crewai.flow.flow import or_, and_

@listen(or_(step_a, step_b))     # fires when EITHER completes
def either_done(self): ...

@listen(and_(step_a, step_b))    # fires only when BOTH have completed
def both_done(self): ...
```

Use `and_` for fan-in (wait for parallel branches to converge before
continuing) and `or_` for "whichever finishes/fires first" semantics.

## Persisting and resuming Flow state

`Flow` supports persisting `self.state` (e.g. to SQLite via
`@persist`/`FlowPersistence`) so a long-running or interrupted flow can
resume rather than restart from scratch — relevant once a flow involves
slow steps (large crew runs, human-in-the-loop pauses) where losing
progress on a crash is costly.

## When to reach for this

Not every multi-crew idea needs a `Flow`. If the logic is genuinely linear
(crew A's output always feeds crew B), just call `.kickoff()` on each crew
in plain Python — a `Flow` earns its complexity when there's real branching,
parallel fan-out/fan-in, or state that needs to survive across steps/pauses.
