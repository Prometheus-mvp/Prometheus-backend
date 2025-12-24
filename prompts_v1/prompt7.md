Role: Agent architect.

Task: Implement v1 LangGraph:

- Worker: retrieve + group + propose actions
- Boss: merge + digest + day plan + proposals

Deliverables:

1. Typed graph state + nodes
2. Tools interfaces:
   - search_events(...)
   - group_threads(...)
   - create_proposal(...)
   - accept/reject proposal
3. Prompt templates + Pydantic outputs:
   - DigestOutput (must cite event_ids)
   - ProposalOutput[]
   - DayPlanOutput
4. Failure handling rules
5. Minimal integration tests for graph.

Constraints:

- No auto-actions without proposal + acceptance.
- Digest must include event_id citations used.
