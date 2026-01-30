import pytest
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient


async def mock_get_db():
    from unittest.mock import Mock

    mock_db = AsyncMock()
    # Mock db.add (synchronous) and db.flush (async) for orchestrator persistence
    mock_db.add = Mock()
    mock_db.flush = AsyncMock()
    yield mock_db


def create_app():
    from app.api.deps import get_db_session, get_user_id
    from app.api.v1.prompts import router as prompts_router

    app = FastAPI()
    app.include_router(prompts_router, prefix="/api/v1")
    app.dependency_overrides[get_db_session] = mock_get_db
    app.dependency_overrides[get_user_id] = lambda: "test-user-id"
    return app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_prompts_missing_intent(client, monkeypatch):
    # Force orchestrator to return unknown intent and mock LLM calls
    from app.agents.base import AgentBase
    from app.agents.orchestrator import AgentOrchestrator

    async def fake_complete_json(self, prompt, schema):
        # Return sources and time range for extractors to skip clarification
        from datetime import datetime, timezone, timedelta
        if "sources" in str(schema):
            return {"sources": ["slack"], "confidence": 0.9, "explicit": True}
        elif "start_time" in str(schema):
            now = datetime.now(timezone.utc)
            return {
                "start_time": (now - timedelta(hours=2)).isoformat(),
                "end_time": now.isoformat(),
                "confidence": 0.9,
                "explicit": True,
            }
        return {}

    # Patch orchestrator.execute_agent to return "unknown" for prompt_router
    # This bypasses the prompt router's normalization that converts "unknown" to "query"
    original_execute_agent = AgentOrchestrator.execute_agent

    async def fake_execute_agent(self, agent_name, agent_method, *args, **kwargs):
        if agent_name == "prompt_router":
            # Return unknown intent directly to test error handling
            return "unknown"
        # For other agents, use original implementation (won't be reached in this test)
        return await original_execute_agent(self, agent_name, agent_method, *args, **kwargs)

    monkeypatch.setattr(AgentOrchestrator, "execute_agent", fake_execute_agent)
    monkeypatch.setattr(AgentBase, "complete_json", fake_complete_json)

    resp = client.post("/api/v1/prompts", json={"prompt": "hi"})
    assert resp.status_code == 400
