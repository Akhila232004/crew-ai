# 10. Deployment & Production

[← back to crew-ai.md](../crew-ai.md)

## Packaging a crew as a service

- **FastAPI wrapper**: expose `POST /run` that calls `crew.kickoff_async(inputs=...)`
  — the natural fit for a crew that responds to on-demand requests (e.g. a
  chat endpoint backed by [scripts/03_chat_with_rag.py](../scripts/03_chat_with_rag.py)'s
  agent). Use `kickoff_async` specifically so the endpoint doesn't block the
  event loop for the duration of the run.
- **CLI**: fine for batch/offline jobs (matches this repo's current
  `scripts/*.py` pattern) — no service to keep running, easiest to reason
  about, easiest to schedule via cron/task scheduler.
- **CrewAI AMP** (managed hosting offered by CrewAI itself): trades
  operational control for not having to run your own service — worth
  evaluating once you're past local experimentation and want hosted
  scheduling/monitoring without building it yourself, but doesn't fit an
  offline/local-Ollama constraint the same way self-hosting does.

## Env/config management

Reuse the pattern already established in
[common/config.py](../common/config.py): a single module that reads
`.env` (or the shared `venkatab-ai-setup/.env`), sets required env vars
(including telemetry opt-outs) **before** `crewai` is imported anywhere,
and exposes typed config values to the rest of the app. Per-environment
settings (dev/staging/prod DB and LLM endpoints) belong in separate `.env`
files or env-var overrides, not hardcoded branches in application code.

## Rate limiting and cost guardrails

- `max_rpm` on `Agent`/`Crew` throttles LLM calls — set this in production
  against your actual provider rate limit, not just to be safe, since
  under-throttling causes failed requests and over-throttling wastes
  latency budget.
- For hosted providers, track `token_usage` per run (see
  [08-llm-integration.md](08-llm-integration.md)) and alert/cap on runs
  that blow past an expected token budget — a runaway agent loop is a cost
  incident, not just a correctness one, once real API billing is involved.
- `max_execution_time` per task is a blunt but effective cap against a
  single stuck task consuming budget indefinitely.

## Error handling & retries around tool/LLM failures

- Tool-level: catch expected failures inside `_run` and return a
  descriptive string rather than raising (see
  [04-tools.md](04-tools.md)) — lets the agent adapt instead of crashing
  the whole run.
- Crew/service level: wrap `kickoff()`/`kickoff_async()` calls in your own
  retry logic for transient infrastructure failures (LLM provider 5xx,
  vector DB timeout) — CrewAI itself doesn't retry a whole crew run for you.
- Task-level guardrails (see [03-tasks.md](03-tasks.md)) handle "the output
  was wrong" retries; infrastructure retries are a separate concern you own
  at the calling layer.

## Scaling

- **Concurrent crews**: each `kickoff()` is independent — running multiple
  crews concurrently is safe as long as underlying resources (DB
  connections, rate-limited LLM endpoints, local Ollama's single-model
  concurrency limits) can actually handle it. Local Ollama in particular
  serializes/contends on GPU memory across concurrent requests — benchmark
  before assuming free concurrency on a local setup.
- **Queueing kickoffs**: for bursty request volume, put an actual queue
  (e.g. a simple DB-backed job table, or Celery/RQ/etc.) in front of crew
  execution rather than firing `kickoff_async` directly from every incoming
  request — keeps you in control of concurrency instead of the LLM
  provider's rate limiter deciding for you via failed requests.
