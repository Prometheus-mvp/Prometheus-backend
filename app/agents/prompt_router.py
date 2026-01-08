"""Prompt router agent using LangChain-style prompt classification."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from app.agents.base import AgentBase

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator


class PromptRouterAgent(AgentBase):
    """Routes user prompts to summarize, task, or query handlers."""

    def __init__(
        self,
        orchestrator: Optional["AgentOrchestrator"] = None,
    ) -> None:
        super().__init__(orchestrator=orchestrator)

    async def classify_intent(
        self, prompt: str
    ) -> Literal["summarize", "task", "query"]:
        """
        Classify the user request intent.
        
        Intent types:
        - summarize: User wants a summary of events/messages
        - task: User wants to see actionable items or tasks
        - query: Open-ended questions, doubts, or information requests
        """
        template = (
            "Classify the user request as one of: summarize, task, query. "
            "Return a JSON object with key intent. "
            "Examples:\n"
            '- "summarize last 2 hours" => summarize\n'
            '- "give me a summary of my slack messages" => summarize\n'
            '- "what needs action" => task\n'
            '- "show me my tasks" => task\n'
            '- "what did John say in Slack?" => query\n'
            '- "why was the meeting cancelled?" => query\n'
            '- "did anyone mention the deadline?" => query\n'
            '- "who sent me an email about the project?" => query\n'
            "- Questions, doubts, or open-ended prompts => query\n"
            f'Prompt: "{prompt}"'
        )
        result = await self.complete_json(
            template, schema={"intent": "string in [summarize, task, query]"}
        )
        intent = result.get("intent", "query")
        if intent not in {"summarize", "task", "query"}:
            # Default to query for unknown/open-ended prompts
            intent = "query"
        return intent  # type: ignore[return-value]


prompt_router = PromptRouterAgent()

__all__ = ["PromptRouterAgent", "prompt_router"]
