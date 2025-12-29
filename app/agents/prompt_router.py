"""Prompt router agent using LangChain-style prompt classification."""

from __future__ import annotations

from typing import Literal

from app.agents.base import AgentBase


class PromptRouterAgent(AgentBase):
    """Routes user prompts to summarize or task handlers."""

    async def classify_intent(
        self, prompt: str
    ) -> Literal["summarize", "task", "unknown"]:
        template = (
            "Classify the user request as one of: summarize, task. "
            "Return a JSON object with key intent. "
            "Examples:\n"
            '- "summarize last 2 hours" => summarize\n'
            '- "what needs action" => task\n'
            "- Otherwise => unknown\n"
            f'Prompt: "{prompt}"'
        )
        result = await self.complete_json(
            template, schema={"intent": "string in [summarize, task, unknown]"}
        )
        intent = result.get("intent", "unknown")
        if intent not in {"summarize", "task"}:
            intent = "unknown"
        return intent  # type: ignore[return-value]


prompt_router = PromptRouterAgent()

__all__ = ["PromptRouterAgent", "prompt_router"]
