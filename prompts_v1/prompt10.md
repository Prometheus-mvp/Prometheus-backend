Role: Frontend lead.

Task: Implement the MVP pages that consume backend contracts, following the strict styles-file rule.

Pages (each must have Page.tsx + Page.styles.ts):

1. ConnectAccountsPage
2. DigestPage
3. ProposalsPage
4. DayPlanPage
5. TasksPage
6. CalendarPage
7. EventDetailDrawer (can be component; if used as page-level, follow page rule)

Deliverables:

- Route map
- For EACH page:
  - Page.tsx skeleton (no Tailwind classes inline)
  - Page.styles.ts exporting all Tailwind classes as an object
- Shared components:
  - Button, Card, SourceBadge, CitationList, ProposalCard
  - Each component may have Component.styles.ts with same rule (no inline Tailwind in TSX)
- Data loading patterns (React Query recommended)
- Error/loading states
- Auth header injection (Supabase JWT)

Constraints:

- Minimal UX but complete.
- Include one example fully coded page (DigestPage) + its styles file.
