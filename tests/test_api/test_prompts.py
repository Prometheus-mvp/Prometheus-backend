import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.prompts import router as prompts_router


def create_app():
    app = FastAPI()
    app.include_router(prompts_router, prefix="/api/v1")
    return app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_prompts_missing_intent(client, monkeypatch):
    # Force classifier to unknown
    from app.agents.prompt_router import prompt_router

    async def fake_classify(prompt):
        return "unknown"

    monkeypatch.setattr(prompt_router, "classify_intent", fake_classify)
    resp = client.post("/api/v1/prompts", json={"prompt": "hi"})
    assert resp.status_code == 400

