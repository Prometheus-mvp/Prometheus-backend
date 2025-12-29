import pytest

from app.agents.summarize_graph import SummarizeAgent
from app.agents.task_graph import TaskAgent


@pytest.mark.asyncio
async def test_summarize_agent(monkeypatch, dummy_session, dummy_vector_results):
    agent = SummarizeAgent()

    async def fake_embed(texts):
        return [[0.1, 0.2]]

    async def fake_search(
        session,
        user_id,
        query_embedding,
        top_k,
        object_types,
        time_start,
        time_end,
        sources,
    ):
        return dummy_vector_results

    async def fake_complete(prompt, schema):
        return {"overview": "ok", "key_events": [], "themes": []}

    monkeypatch.setattr(agent.embedding_service, "embed_text", fake_embed)
    monkeypatch.setattr(agent.vector_store, "search", fake_search)
    monkeypatch.setattr(agent, "complete_json", fake_complete)

    result = await agent.summarize(dummy_session, user_id="u1", prompt="summarize")
    assert result["overview"] == "ok"
    # Summary object was added to session
    assert dummy_session.added, "Summary was not added to session"


@pytest.mark.asyncio
async def test_task_agent(monkeypatch, dummy_session, dummy_vector_results):
    agent = TaskAgent()

    async def fake_embed(texts):
        return [[0.1, 0.2]]

    async def fake_search(
        session,
        user_id,
        query_embedding,
        top_k,
        object_types,
        time_start,
        time_end,
        sources,
    ):
        return dummy_vector_results

    async def fake_complete(prompt, schema):
        return {"tasks": [{"title": "Do it", "priority": "high", "details": "X"}]}

    monkeypatch.setattr(agent.embedding_service, "embed_text", fake_embed)
    monkeypatch.setattr(agent.vector_store, "search", fake_search)
    monkeypatch.setattr(agent, "complete_json", fake_complete)

    result = await agent.detect_tasks(
        dummy_session, user_id="u1", prompt="what needs action"
    )
    assert result["tasks"][0]["title"] == "Do it"
    assert dummy_session.added, "Task was not added to session"
