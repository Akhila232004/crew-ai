# 1. Foundations

[← back to crew-ai.md](../crew-ai.md)

## What is CrewAI vs. LangChain/LangGraph/AutoGen

CrewAI is a standalone, opinionated **multi-agent orchestration framework** —
it does not sit on top of LangChain (it did originally, but has since been
rewritten to have no LangChain dependency). It trades some flexibility for a
much shorter path to a working multi-agent system.

| Framework | Mental model | Best fit |
|---|---|---|
| **CrewAI** | Role-playing agents (`role`/`goal`/`backstory`) collaborating on `Task`s via a `Process` | Business-process-shaped work: research → draft → review pipelines, role-based delegation |
| **LangGraph** | Explicit state graph — you define nodes/edges yourself | Fine-grained control over control flow, cycles, custom state machines |
| **AutoGen** | Conversable agents that message each other | Open-ended multi-agent conversation/negotiation patterns |
| **LangChain** | Chains/runnables — general LLM app building blocks | Low-level building blocks, not agent orchestration per se |

Rule of thumb: reach for CrewAI when the workflow maps naturally onto "a team
of specialists each responsible for part of the job." Reach for LangGraph
when you need explicit, arbitrary control flow (loops, retries, branching)
that doesn't fit CrewAI's `Process` abstractions. CrewAI's `Flow` (see
[07-flows.md](07-flows.md)) narrows this gap by adding graph-like
orchestration on top of Crews.

## Core architecture

```
Crew
 ├─ Agent(s)      — role, goal, backstory, llm, tools
 ├─ Task(s)       — description, expected_output, assigned agent, context
 ├─ Process       — sequential | hierarchical (how tasks are executed)
 └─ kickoff()     — runs the crew, returns CrewOutput

Flow
 ├─ @start / @listen / @router  — event-driven steps
 ├─ state                        — Pydantic model, shared across steps
 └─ can invoke one or more Crews as steps
```

- **Agent** — an LLM configured with a persona and (optionally) tools and memory.
- **Task** — a unit of work with a description and an expected output, assigned to one agent.
- **Crew** — a set of agents + tasks + a process for running them together.
- **Process** — the execution strategy: `sequential` (task order = execution order) or `hierarchical` (a manager LLM plans and delegates).
- **Flow** — a higher-level orchestrator for event-driven, stateful pipelines that can wire multiple Crews together with branching logic.

The core insight: **role and goal text materially affects output quality**,
because it becomes part of every prompt CrewAI builds for that agent. Treat
`role`/`goal`/`backstory` as prompt engineering, not documentation.

## Project scaffolding

See [Installation](../crew-ai.md#installation) in the main file for the
install steps. `crewai create crew <name>` generates:

```
<name>/
  src/<name>/
    config/
      agents.yaml
      tasks.yaml
    crew.py       # @CrewBase class wiring agents/tasks together
    main.py        # entry point calling crew().kickoff(inputs=...)
  pyproject.toml
  .env
```

This repo doesn't use that scaffold — [scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py)
defines everything directly in Python, which is the right call for a single-agent
script. Reach for the YAML-driven scaffold once you have multiple agents/tasks
that benefit from being edited without touching Python.

## CrewAI CLI

| Command | Purpose |
|---|---|
| `crewai create crew <name>` | Scaffold a new project |
| `crewai run` | Run the crew defined in the current project |
| `crewai train -n <iterations>` | Iteratively refine agent behavior against human feedback |
| `crewai test -n <iterations>` | Evaluate crew output quality against a model-graded rubric |
| `crewai replay -t <task_id>` | Re-run from a specific task using cached prior outputs (fast iteration) |
| `crewai log-tasks-outputs` | Dump the outputs of the last run |
| `crewai reset-memories` | Clear short/long-term/entity memory stores |

## Config-driven setup: YAML vs. Python

**YAML (`agents.yaml` + `tasks.yaml`)** — declarative, non-engineers can edit
prompts without touching code, plays well with `crewai train`/`test`. Use
`{variable}` placeholders filled from `kickoff(inputs={...})`.

```yaml
# agents.yaml
researcher:
  role: "{topic} Senior Researcher"
  goal: "Uncover cutting-edge developments in {topic}"
  backstory: "You're a veteran researcher known for finding the signal in the noise."
```

**Python** — full programmatic control, easier to unit test, easier to branch
agent/task construction on runtime conditions. This repo's
[scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py) uses this style
because there's exactly one agent and the tool wiring is code-driven anyway.

Default to YAML once a project has 3+ agents or you want non-code
iteration on prompts; stay in Python for small/dynamic setups.
