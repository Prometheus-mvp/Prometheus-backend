# Prometheus v1 Backend — Setup Guide

## Prerequisites
- Python 3.11
- Postgres with pgvector extension (Supabase recommended)
- Redis (Upstash-compatible) for RQ jobs
- OpenAI API key
- Slack app (OAuth v2), Telegram API ID/HASH (MTProto), Outlook Azure app (Microsoft Graph)

## 1) Clone & Install
```bash
pip install -r requirements.txt
```

## 2) Environment
Create `.env` from `.env.example` and fill:
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
- DATABASE_URL (postgresql://... )
- REDIS_URL
- OPENAI_API_KEY
- ENCRYPTION_KEY (32-byte hex, `openssl rand -hex 32`)
- Slack: SLACK_CLIENT_ID / SECRET / REDIRECT_URI
- Telegram: TELEGRAM_API_ID / TELEGRAM_API_HASH
- Outlook: OUTLOOK_CLIENT_ID / SECRET / REDIRECT_URI / TENANT_ID

## 3) Database & Migrations
```bash
alembic upgrade head
```
Then apply RLS policies in Supabase SQL editor:
```
alembic/versions/002_rls_policies.sql
```

## 4) Run Services
API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Worker (RQ):
```bash
python -m app.jobs.worker
```

## 5) Connectors
- Slack: GET `/api/v1/connectors/slack/oauth/initiate` → user auth → callback stores encrypted tokens.
- Telegram: POST `/api/v1/connectors/telegram/auth/initiate` (phone), then `/verify` with code/hash/phone_number.
- Outlook: GET `/api/v1/connectors/outlook/oauth/initiate` → user auth → callback stores tokens.

## 6) Prompt & Tasks
- POST `/api/v1/prompts` → routes to summarize/task agents via prompt router.
- GET `/api/v1/tasks` (filters: status, priority).
- Calendar CRUD under `/api/v1/calendar/events`.

## 7) Jobs
- Ingestion: `app/jobs/ingestion.py` (poll connectors, idempotent insert).
- Embedding: `app/jobs/embedding.py` (OpenAI embeddings → pgvector).
- Summarization: `app/jobs/summarization.py`.
- Retention: `app/jobs/retention.py`.
- Worker bootstrap: `app/jobs/worker.py`.

## 8) Production Hardening Checklist
- Enable pgvector extension.
- Apply RLS policies.
- Configure HTTPS, secure secrets, and logging sinks.
- Add retry/backoff for connector HTTP/Telethon calls; handle rate limits.
- Token refresh: Slack/Outlook implemented; add telemetry/alerts.
- Run migrations in CI/CD; add health checks and liveness probes.
- Tests: add unit/integration for agents, API, jobs, token refresh, RLS.
- Observability: structured JSON logs, metrics, error tracking (e.g., Sentry).

## 9) Testing (recommended)
```bash
pytest --maxfail=1 -q
```
(Add mocks for external APIs; aim for ≥90% coverage.)

