"""Source Extractor Agent - Extracts source applications from prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.agents.base import AgentBase

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator

# Valid sources in the system
VALID_SOURCES = ["slack", "telegram", "outlook", "calendar"]


class SourceExtractor(AgentBase):
    """Extract source applications from user prompts."""

    def __init__(
        self,
        orchestrator: Optional["AgentOrchestrator"] = None,
    ) -> None:
        super().__init__(orchestrator=orchestrator)

    async def extract_sources(self, prompt: str) -> Dict[str, Any]:
        """
        Extract sources (slack, telegram, outlook) from prompt.

        Returns:
            {
                "sources": ["slack", "telegram"],  # List of identified sources
                "confidence": 0.9,  # Confidence in extraction
                "explicit": True,  # Whether sources were explicitly mentioned
            }
        """
        # First try simple keyword matching
        prompt_lower = prompt.lower()
        found_sources = []

        source_keywords = {
            "slack": ["slack", "channel", "dm", "direct message"],
            "telegram": ["telegram", "tg", "telethon"],
            "outlook": ["outlook", "email", "mail", "inbox", "microsoft"],
            "calendar": ["calendar", "meeting", "appointment", "schedule"],
        }

        for source, keywords in source_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                found_sources.append(source)

        if found_sources:
            return {
                "sources": found_sources,
                "confidence": 0.95,
                "explicit": True,
            }

        # Use LLM for more nuanced extraction
        llm_prompt = f"""
Extract which communication applications/sources the user is referring to.
Valid sources: slack, telegram, outlook, calendar

User prompt: "{prompt}"

Return JSON with:
- sources: list of identified sources (empty if none identified)
- confidence: float 0-1 indicating confidence
- explicit: boolean indicating if sources were explicitly mentioned

If no sources are mentioned or implied, return an empty sources list.
"""

        result = await self.complete_json(
            llm_prompt,
            schema={
                "sources": "array",
                "confidence": "number",
                "explicit": "boolean",
            },
        )

        # Validate and filter sources
        raw_sources = result.get("sources", [])
        valid_sources = [s.lower() for s in raw_sources if s.lower() in VALID_SOURCES]

        return {
            "sources": valid_sources,
            "confidence": result.get("confidence", 0.5),
            "explicit": result.get("explicit", False),
        }


# Module-level singleton
source_extractor = SourceExtractor()

__all__ = ["SourceExtractor", "source_extractor", "VALID_SOURCES"]
