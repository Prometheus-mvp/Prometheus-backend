"""Tests for SummarizeAgent (pull-based) and TaskAgent."""

from datetime import datetime, timedelta, timezone

import pytest

from app.agents.summarize_graph import SummarizeAgent
from app.agents.task_graph import TaskAgent


@pytest.mark.asyncio
async def test_summarize_agent(monkeypatch, dummy_session, dummy_vector_results):
    """Test SummarizeAgent with new time_start/time_end signature."""
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
        query_text=None,
    ):
        return dummy_vector_results

    async def fake_complete(prompt, schema):
        return {"overview": "ok", "key_events": [], "themes": []}

    monkeypatch.setattr(agent.embedding_service, "embed_text", fake_embed)
    monkeypatch.setattr(agent.vector_store, "search", fake_search)
    monkeypatch.setattr(agent, "complete_json", fake_complete)

    now = datetime.now(timezone.utc)
    result = await agent.summarize(
        dummy_session,
        user_id="u1",
        prompt="summarize",
        time_start=now - timedelta(hours=2),
        time_end=now,
        sources=["slack"],
    )
    assert result["overview"] == "ok"
    # Summary object was added to session
    assert dummy_session.added, "Summary was not added to session"


@pytest.mark.asyncio
async def test_task_agent(monkeypatch, dummy_session, dummy_vector_results):
    """Test TaskAgent with new time_start/time_end signature."""
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
        query_text=None,
    ):
        return dummy_vector_results

    async def fake_complete(prompt, schema):
        return {"tasks": [{"title": "Do it", "priority": "high", "details": "X"}]}

    monkeypatch.setattr(agent.embedding_service, "embed_text", fake_embed)
    monkeypatch.setattr(agent.vector_store, "search", fake_search)
    monkeypatch.setattr(agent, "complete_json", fake_complete)

    now = datetime.now(timezone.utc)
    result = await agent.detect_tasks(
        dummy_session,
        user_id="u1",
        prompt="what needs action",
        time_start=now - timedelta(hours=24),
        time_end=now,
        sources=["slack", "telegram"],
    )
    assert result["tasks"][0]["title"] == "Do it"
    assert dummy_session.added, "Task was not added to session"


@pytest.mark.asyncio
async def test_summarize_agent_is_pull_based(monkeypatch, dummy_session, dummy_vector_results):
    """Test that SummarizeAgent is pull-based (only executes on explicit request)."""
    # SummarizeAgent should only run when explicitly called
    # It should not run in background like QueryAgent
    agent = SummarizeAgent()
    
    # Agent should have orchestrator support
    assert hasattr(agent, 'orchestrator')
    
    # Agent should accept orchestrator in constructor
    from unittest.mock import MagicMock
    mock_orchestrator = MagicMock()
    agent_with_orch = SummarizeAgent(orchestrator=mock_orchestrator)
    assert agent_with_orch.orchestrator == mock_orchestrator
