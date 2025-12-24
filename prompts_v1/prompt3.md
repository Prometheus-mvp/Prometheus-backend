Role: Security engineer (Supabase).

Task: Provide RLS policies for all v1 tables.

Deliverables:

1. SQL statements to enable RLS per table
2. Policies:
   - user can CRUD only their rows
   - service role bypass notes (backend-only operations)
3. Guidance on mapping auth.uid() to users.id and ensuring backend writes correct user_id

Output:

- One SQL file: rls.sql
- Steps to apply in Supabase

Constraints:

- Minimal policies, no overly broad access.
- Include a quick audit checklist.
