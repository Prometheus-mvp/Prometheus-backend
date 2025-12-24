Role: Data/ML engineer.

Task: Define pipeline from ingested payload -> normalized events + entities + urgency/actionability.

Deliverables:

1. Pydantic schemas:
   EventIngested, NormalizedEvent, Entity, ActionCandidate
2. Rule-based extraction first + LLM-assisted strict JSON extraction
3. Embedding generation strategy (when, which text)
4. 10 unit test fixtures (pytest)
5. No DB changes unless necessary; if necessary add Alembic revision.

Constraints:

- Deterministic + testable.
- No hallucinations: entities must be grounded in event text.
