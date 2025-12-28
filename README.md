# Prometheus v1 Backend

Production-grade FastAPI backend with Supabase Postgres (pgvector), Redis RQ jobs, OpenAI embeddings, LangGraph-style agents, and connectors for Slack, Telegram (Telethon MTProto), and Outlook (Microsoft Graph).

## Quick Start
1) Python 3.11, Postgres with pgvector, Redis.
2) Create `.env` from `.env.example` (fill Supabase, DB, Redis, OpenAI, Slack/Telegram/Outlook, ENCRYPTION_KEY).
3) Install deps:
```bash
pip install -r requirements.txt
```
4) Migrations + RLS:
```bash
alembic upgrade head
# then run RLS SQL in Supabase: alembic/versions/002_rls_policies.sql
```
5) Run API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
6) Run worker (RQ):
```bash
python -m app.jobs.worker
```

## Endpoints (v1)
- Connectors: `/api/v1/connectors/*` (Slack/Outlook OAuth, Telegram auth, list/delete).
- Prompts: `POST /api/v1/prompts` (routes to summarize/task agents).
- Tasks: `GET /api/v1/tasks`.
- Calendar: CRUD under `/api/v1/calendar/events`.
- Health: `/health`.

## Jobs
- Ingestion: `app/jobs/ingestion.py` (poll connectors, idempotent inserts).
- Embedding: `app/jobs/embedding.py` (OpenAI embeddings → pgvector).
- Summarization: `app/jobs/summarization.py`.
- Retention: `app/jobs/retention.py`.
- Worker bootstrap: `app/jobs/worker.py` (Redis URL from env).

## Architecture
- FastAPI app (`app/main.py`) with v1 router.
- Core: config/logging/security/crypto.
- DB: SQLAlchemy async, pgvector embeddings, RLS-ready schema via Alembic.
- Services: connectors, vector store, embedding service.
- Agents: prompt router, summarize, task detection (LLM JSON mode).
- Tests skeleton under `tests/`.

## Test Coverage

The project maintains **90%+ test coverage** across all modules. See `docs/TESTING.md` for details.

Run tests:
```bash
pytest                                    # All tests
pytest --cov=app --cov-report=html       # With coverage report
```

## Documentation

- `docs/SETUP.md` - Complete setup guide
- `docs/RUNBOOK.md` - Operations playbook  
- `docs/TESTING.md` - Testing guide
- `PROJECT_COMPLETE.md` - Project summary

## Notes
- Token refresh implemented for Slack and Outlook; Telegram uses Telethon session string (MTProto) with code verification safeguards.
- RLS SQL must be applied in Supabase after migrations.
- Error handling: connectors wrapped with HTTP/Telethon error handling; prompts/agents wrap failures with 500s and log details; OpenAI/embedding calls raise explicit errors.
- Replace placeholder scopes/limits as needed for production; add additional retries/backoff and observability as desired.