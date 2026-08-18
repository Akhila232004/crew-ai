# 11. Applied Projects (build to learn)

[← back to crew-ai.md](../crew-ai.md)

Each project below names the topics it exercises so you can tell which
gaps it's meant to close. Build in order — later projects assume the
patterns from earlier ones.

## 1. Research crew (sequential)

**Exercises**: [01-foundations.md](01-foundations.md), [02-agents.md](02-agents.md), [03-tasks.md](03-tasks.md), [05-crews-process.md](05-crews-process.md)

Web-search agent → summarizer agent → writer agent, `Process.sequential`,
chained via `Task.context`. Keep it to 3 agents/tasks — the point is to
feel `context` chaining and `expected_output` phrasing, not build something
elaborate.

- Acceptance: running with a different `{topic}` input produces a
  noticeably different, on-topic final post without touching any code.
- Stretch: swap the writer agent's `llm` to a different model than the
  researcher's and compare output quality/latency.

## 2. Hierarchical crew

**Exercises**: [05-crews-process.md](05-crews-process.md)

3+ specialist agents (e.g. researcher, data-analyst, writer) under
`Process.hierarchical`, either with the auto-manager or a custom
`manager_agent`.

- Acceptance: log/inspect the manager's delegation decisions (`verbose=True`)
  and confirm task-to-agent assignment actually varies sensibly based on
  task content, not just always picking the first agent.
- Stretch: compare total token usage / latency vs. the equivalent
  sequential crew — hierarchical isn't free.

## 3. RAG-powered crew

**Exercises**: [04-tools.md](04-tools.md), [06-memory-knowledge.md](06-memory-knowledge.md)

Point an agent's custom tool at the existing Qdrant/Postgres RAG pipeline
in this repo rather than building a new retriever — this is exactly what
[scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py) already does
for `product_catalog`.

- Acceptance (if starting from scratch): agent must call the tool before
  answering catalog questions, and answers should not hallucinate products
  not present in the retrieved context.
- Stretch: extend to the `order_support` document type described but not
  yet implemented in [rag-building.md §9](../rag-building.md#9-open-questions-to-resolve-before-implementation),
  giving the crew two tools (catalog + orders) and see whether the agent
  picks the right one per question.

## 4. Flow-based multi-crew pipeline

**Exercises**: [07-flows.md](07-flows.md)

A `Flow` with a classification `@start` step, an `@router` branching on
that classification, and two different downstream Crews depending on the
branch (e.g. "simple lookup" crew vs. "deep research" crew).

- Acceptance: both branches are actually reachable and produce
  meaningfully different execution paths (log which branch fired per run).
- Stretch: add `@persist` state so the flow can resume after being killed
  mid-run.

## 5. Human-in-the-loop approval crew

**Exercises**: [03-tasks.md](03-tasks.md)

A crew that drafts a final action (an email, a file write, a support
reply) with `human_input=True` on the final task, so a human must approve
or request revisions before anything with a real side effect happens.

- Acceptance: rejecting/editing the draft actually changes the agent's
  next attempt, not just re-shows the same output.
- Stretch: replace the human approval with a `guardrail` that
  auto-approves only if certain hard constraints are met, and only falls
  back to human input otherwise.

## 6. Add tracing/eval

**Exercises**: [09-testing-observability.md](09-testing-observability.md)

Pick any crew above and add either a tracing integration (Langfuse/AgentOps/OTel)
or a small custom eval script (`kickoff()` N times, score against a
rubric), then deliberately change a prompt (role/goal/backstory or
`expected_output`) and measure the before/after difference quantitatively
instead of eyeballing it.

- Acceptance: you can point at a specific number (score, token count,
  latency) that changed as a result of the prompt edit, not just a
  subjective impression.
