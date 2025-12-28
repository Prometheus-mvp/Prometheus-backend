"""Base agent utilities and LLM client setup."""
from __future__ import annotations

import logging
from typing import Any, Dict

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings


class AgentBase:
    """Base utilities for agents."""

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

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
            import json
            return json.loads(content)
        except OpenAIError as exc:
            self.logger.error("LLM call failed", extra={"error": str(exc)})
            raise RuntimeError("LLM request failed") from exc
        except Exception as exc:  # json parsing / other
            self.logger.error("LLM response parsing failed", extra={"error": str(exc)})
            raise RuntimeError("LLM response invalid") from exc


__all__ = ["AgentBase"]

