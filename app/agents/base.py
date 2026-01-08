"""Base agent utilities and LLM client setup."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator


class AgentBase:
    """Base utilities for agents with orchestrator support."""

    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        orchestrator: Optional["AgentOrchestrator"] = None,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.orchestrator = orchestrator  # For inter-agent communication

    async def complete_json(
        self, prompt: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call the LLM in JSON mode.
        Expects strict JSON conforming to the provided schema.
        """
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a structured JSON responder.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            content = resp.choices[0].message.content
            if not content:
                return {}

            return json.loads(content)
        except OpenAIError as exc:
            self.logger.error("LLM call failed", extra={"error": str(exc)})
            raise RuntimeError("LLM request failed") from exc
        except Exception as exc:  # json parsing / other
            self.logger.error("LLM response parsing failed", extra={"error": str(exc)})
            raise RuntimeError("LLM response invalid") from exc

    async def get_other_agent_result(
        self,
        agent_name: str,
        time_window_hours: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve result from another agent for use as context.
        
        Example: QueryAgent can get SummarizeAgent result to answer questions.
        SummarizeAgent can get QueryAgent result for fine-grained context.
        """
        if not self.orchestrator:
            return None
        return await self.orchestrator.get_agent_result(agent_name, time_window_hours)


__all__ = ["AgentBase"]
