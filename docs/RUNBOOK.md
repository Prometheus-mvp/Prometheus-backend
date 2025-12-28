# Prometheus v1 Backend — Runbook

## Operations
- Start API: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Start worker: `python -m app.jobs.worker`
- Apply migrations: `alembic upgrade head`
- Apply RLS (Supabase SQL editor): `alembic/versions/002_rls_policies.sql`

## Common Tasks
- Rotate encryption key: set new `ENCRYPTION_KEY`, re-encrypt tokens as needed.
- Token refresh failures: check Slack/Outlook refresh flows; re-auth user if both access/refresh invalid.
- Backpressure: scale Redis/worker count; adjust RQ queues.
- Cleanup: run retention job `app/jobs/retention.py` to remove expired events/embeddings.

## Health Checks
- API: `/health`
- Redis/RQ: monitor queue depth; worker logs.
- Database: ensure pgvector extension enabled.

## Logs & Metrics
- Structured JSON logging via `app/core/logging.py`.
- Add error tracking (e.g., Sentry) and metrics (request latency, queue depth) in production.

## Security
- RLS enforced; service role only server-side.
- Tokens encrypted (AES-256-GCM).
- HTTPS/TLS everywhere; secure secrets storage (vault).

## Incident Playbook (examples)
- Connectors down: pause ingestion queue; increase retries/backoff; alert.
- OpenAI errors: exponential backoff, fall back or retry later.
- DB slow/locks: check long-running queries, reduce batch sizes (ingestion/retention).
- Redis unavailable: API still runs; background work paused—restore Redis, then re-queue jobs.

