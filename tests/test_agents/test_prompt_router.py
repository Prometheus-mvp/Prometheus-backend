import pytest

from app.agents.prompt_router import PromptRouterAgent


@pytest.mark.asyncio
async def test_prompt_router_classify(monkeypatch):
    agent = PromptRouterAgent()

    async def fake_complete(prompt, schema):
        return {"intent": "summarize"}

    monkeypatch.setattr(agent, "complete_json", fake_complete)
    intent = await agent.classify_intent("summarize last 2 hours")
    assert intent == "summarize"

