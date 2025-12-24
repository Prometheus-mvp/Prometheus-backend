Role: Frontend platform engineer.

Task: Build the API layer + typing strategy.

Deliverables:

1. src/api/client.ts:
   - baseURL
   - fetch wrapper
   - auth header injection from Supabase session
   - retry/backoff basics
2. src/api/endpoints.ts:
   - typed functions: getDigest, getProposals, acceptProposal, rejectProposal, getDayPlan, CRUD tasks/calendar
3. src/types/\*:
   - Event, DigestResponse, Proposal, DayPlan, Task, CalendarEvent
4. React Query setup:
   - QueryClient
   - caching keys
   - invalidation strategy on accept/reject
5. API error normalization (single shape)

Constraints:

- No inline Tailwind in any TSX (styles file rule still applies for UI).
- Be explicit about pagination and ranges.
