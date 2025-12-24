Role: Database + backend engineer.

Task: Generate:
A) SQLAlchemy 2.0 models (typed, relationships)
B) Alembic revision 0001 creating:

- pgvector extension
- all core tables + indexes
- unique constraints for dedupe keys where needed
- expires_at index for retention cleanup
- search readiness (either FTS columns or a clear plan)

Output requirements:

- Exact files:
  - app/db/base.py, app/db/session.py
  - app/models/\*.py
  - alembic/env.py updates for autogenerate
  - alembic/versions/0001_initial.py
- Commands to run migrations locally.
- Migration rules checklist.

Assumptions:

- UUID PKs
- UTC timestamps
- JSONB for metadata/raw payload
- Retention via expires_at + scheduled cleanup job
