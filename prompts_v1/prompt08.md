Role: API designer.

Task: Define stable REST endpoints + schemas:

- GET /digest?range=120m&scope=personal,professional
- GET /proposals?status=pending
- POST /proposals/{id}/accept
- POST /proposals/{id}/reject
- GET /day-plan?date=YYYY-MM-DD
- CRUD /tasks, /calendar-events, /notes
- GET /events/search (filters + pagination)

Deliverables:

- OpenAPI-like spec + JSON examples + error codes
- Auth model (Supabase JWT)
- Versioning strategy (v1 prefix or header)
- Rate limits and pagination standard

Constraints:

- Minimal and consistent.
- No chat endpoint required in v1.
