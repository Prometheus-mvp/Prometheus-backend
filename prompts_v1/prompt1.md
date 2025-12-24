Role: Backend Tech Lead.

Task: Produce the complete backend blueprint for Prometheus v1 using FastAPI + SQLAlchemy + Alembic + Supabase Postgres (pgvector) + Redis + LangGraph + OpenAI.

Deliverables:

1. Architecture diagram (ASCII ok) + key design decisions
2. Backend folder structure including:
   - app/
   - app/core/ (config, logging, security)
   - app/db/ (engine, session, base)
   - app/models/
   - app/schemas/
   - app/api/ (routers, deps)
   - app/services/ (connectors, embeddings, summarizer)
   - app/agents/ (LangGraph)
   - app/jobs/ (workers, schedulers)
   - tests/
   - alembic/ + alembic.ini
3. Alembic setup instructions + commands (init/revision/upgrade)
4. Initial DB model list:
   users, linked_accounts, oauth_tokens,
   events, entities, threads,
   tasks, calendar_events, notes,
   summaries, proposals, drafts
5. API endpoint list + request/response examples
6. Background jobs list + triggers (ingestion, embedding, summarization, retention cleanup)
7. Security/privacy model (Supabase RLS, encryption at rest/in transit, token encryption, retention)
8. Week 1–4 milestones

Constraints:

- Two connectors only (Slack + Google Calendar default).
- Must support: “summarize last 2 hours”, “what needs action?”, “plan my day”.
- Every schema change must be an Alembic migration.
- Include a “production readiness checklist” (12–20 bullets).
