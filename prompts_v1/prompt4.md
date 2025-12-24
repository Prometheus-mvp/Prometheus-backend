Role: Integrations engineer.

Task: Implement Slack ingestion design.

Deliverables:

1. Required Slack scopes + event subscriptions
2. FastAPI route:
   - POST /webhooks/slack/events
   - request signing verification
3. Idempotency design:
   - event_id unique constraint + retries safe
4. Normalization to Event schema + DB write path
5. Job triggers: embedding + optional thread expansion
6. If DB changes required, include Alembic revision 0002.

Constraints:

- Store minimal fields; raw payload optional.
- Securely map Slack workspace/user to linked_accounts.
