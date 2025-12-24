Role: Integrations engineer.

Task: Build Google Calendar integration.

Deliverables:

1. OAuth scopes + consent notes
2. Endpoints:
   - GET /auth/google/start
   - GET /auth/google/callback
3. Sync job:
   - fetch next 7 days + updates
4. Normalize to Event schema
5. Optional write-back: only for accepted proposals, disabled by default
6. If DB changes required, Alembic revision 0003.

Constraints:

- Token refresh stored encrypted.
- Two-way sync guarded by explicit user setting.
- Include rate limiting/backoff notes.
