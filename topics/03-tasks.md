# 3. Tasks

[← back to crew-ai.md](../crew-ai.md)

## Anatomy of a Task

```python
from crewai import Task

research_task = Task(
    description="Research the latest developments in {topic}. Focus on the last 6 months.",
    expected_output="A bullet list of 5-10 findings, each with a source.",
    agent=researcher,
)
```

`expected_output` matters as much as `description` — it's the strongest
lever CrewAI gives you over output shape/length/format without resorting to
`output_json`. Be concrete ("a bullet list of 5-10 findings, each with a
source") rather than vague ("a summary of findings").

## `context` — chaining task outputs

```python
writing_task = Task(
    description="Write a blog post based on the research findings.",
    expected_output="A 500-word blog post in markdown.",
    agent=writer,
    context=[research_task],   # output of research_task is injected into this task's prompt
)
```

This is how CrewAI implements pipelines without you manually passing strings
around — `context` is a list of prior `Task` objects whose `.output` gets
concatenated into this task's prompt. In `Process.sequential`, tasks also
implicitly see prior task outputs in order even without explicit `context`,
but declaring `context` explicitly documents the dependency and matters more
once you have non-linear task graphs or hierarchical process.

## Structured output: `output_json` / `output_pydantic`

```python
from pydantic import BaseModel

class Finding(BaseModel):
    claim: str
    source: str

class ResearchOutput(BaseModel):
    findings: list[Finding]

research_task = Task(
    description="...",
    expected_output="A list of findings with sources.",
    agent=researcher,
    output_pydantic=ResearchOutput,
)
```

Use this whenever a downstream task, tool, or your own code needs to parse
the result programmatically rather than read it as prose — e.g. feeding a
task's output into a database write or an API call. `output_json` gives you
a plain dict when you don't want to define a Pydantic model.

## `output_file`

`output_file="report.md"` writes the task's final output to disk as a side
effect — handy for artifacts you want to inspect or version outside the
crew run itself (e.g. audit trails, generated reports).

## Sync vs. async tasks

`async_execution=True` lets a task run in the background while
`Process.sequential` moves on — useful when two independent tasks (e.g. two
unrelated research lookups) don't depend on each other and can run
concurrently before a later task consumes both via `context`. Tasks with
dependencies via `context` are automatically awaited before the dependent
task starts.

## Conditional tasks and guardrails

`ConditionalTask` only executes if a condition function (evaluated against
prior task output) returns `True` — useful for branch-only-if-needed steps
(e.g. only run a "escalate to human" task if a classification task flagged
risk). `guardrail` on a `Task` is a validation function run against the
output before it's accepted; on failure CrewAI retries the task with
feedback about what was wrong, up to `max_retries`.

```python
def validate_length(output: TaskOutput) -> tuple[bool, str]:
    if len(output.raw) > 2000:
        return False, "Output exceeds 2000 characters, please shorten."
    return True, output.raw

writing_task = Task(..., guardrail=validate_length)
```

Guardrails are the cheapest way to enforce hard constraints (length, format,
banned content) without fully switching to `output_pydantic`.

## Human-in-the-loop tasks

`human_input=True` pauses execution after the agent produces a draft output
and prompts for human feedback via stdin before the task is marked complete
— the agent then revises based on that feedback. Good for a final
approval/edit step before anything is sent, published, or executed with
real-world side effects. See the applied project idea in
[11-applied-projects.md](11-applied-projects.md).
