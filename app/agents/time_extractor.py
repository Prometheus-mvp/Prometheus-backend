"""Time Range Extractor - Extracts time ranges from natural language prompts."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from app.agents.base import AgentBase

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator


class TimeRangeExtractor(AgentBase):
    """Extract time ranges from natural language prompts."""

    def __init__(
        self,
        orchestrator: Optional["AgentOrchestrator"] = None,
    ) -> None:
        super().__init__(orchestrator=orchestrator)

    async def extract_time_range(
        self,
        prompt: str,
    ) -> Dict[str, Any]:
        """
        Extract start_time and end_time from prompt.
        
        Parses natural language like:
        - "last 2 hours"
        - "yesterday"
        - "Jan 1 to Jan 5"
        - "this week"
        - "past 24 hours"
        
        Returns:
            {
                "start_time": datetime or None,
                "end_time": datetime or None,
                "confidence": float 0-1,
                "explicit": bool,
            }
        """
        now = datetime.now(timezone.utc)
        prompt_lower = prompt.lower()

        # Try simple pattern matching first
        result = self._try_simple_patterns(prompt_lower, now)
        if result["start_time"] and result["end_time"]:
            return result

        # Use LLM for more complex parsing
        return await self._llm_extract(prompt, now)

    def _try_simple_patterns(
        self, prompt: str, now: datetime
    ) -> Dict[str, Any]:
        """Try simple regex patterns for common time expressions."""
        # Pattern: "last N hours"
        match = re.search(r"last\s+(\d+)\s*hours?", prompt)
        if match:
            hours = int(match.group(1))
            return {
                "start_time": now - timedelta(hours=hours),
                "end_time": now,
                "confidence": 0.95,
                "explicit": True,
            }

        # Pattern: "last N days"
        match = re.search(r"last\s+(\d+)\s*days?", prompt)
        if match:
            days = int(match.group(1))
            return {
                "start_time": now - timedelta(days=days),
                "end_time": now,
                "confidence": 0.95,
                "explicit": True,
            }

        # Pattern: "past N hours"
        match = re.search(r"past\s+(\d+)\s*hours?", prompt)
        if match:
            hours = int(match.group(1))
            return {
                "start_time": now - timedelta(hours=hours),
                "end_time": now,
                "confidence": 0.95,
                "explicit": True,
            }

        # Pattern: "today"
        if "today" in prompt:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return {
                "start_time": start,
                "end_time": now,
                "confidence": 0.9,
                "explicit": True,
            }

        # Pattern: "yesterday"
        if "yesterday" in prompt:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return {
                "start_time": start,
                "end_time": end,
                "confidence": 0.9,
                "explicit": True,
            }

        # Pattern: "this week"
        if "this week" in prompt:
            # Start of week (Monday)
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return {
                "start_time": start,
                "end_time": now,
                "confidence": 0.9,
                "explicit": True,
            }

        # Pattern: "last week"
        if "last week" in prompt:
            days_since_monday = now.weekday()
            this_monday = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            last_monday = this_monday - timedelta(days=7)
            return {
                "start_time": last_monday,
                "end_time": this_monday,
                "confidence": 0.9,
                "explicit": True,
            }

        # No match
        return {
            "start_time": None,
            "end_time": None,
            "confidence": 0.0,
            "explicit": False,
        }

    async def _llm_extract(
        self, prompt: str, now: datetime
    ) -> Dict[str, Any]:
        """Use LLM for complex time extraction."""
        llm_prompt = f"""
Extract the time range from the user's request.
Current time: {now.isoformat()}

User prompt: "{prompt}"

Return JSON with:
- start_time: ISO format datetime string or null if not specified
- end_time: ISO format datetime string or null if not specified  
- confidence: float 0-1 indicating confidence in extraction
- explicit: boolean indicating if time was explicitly mentioned

If no time range is specified, return null for both start_time and end_time.
Always ensure end_time > start_time if both are specified.
"""

        result = await self.complete_json(
            llm_prompt,
            schema={
                "start_time": "string",
                "end_time": "string",
                "confidence": "number",
                "explicit": "boolean",
            },
        )

        # Parse datetime strings
        start_time = None
        end_time = None

        if result.get("start_time"):
            try:
                start_time = datetime.fromisoformat(
                    result["start_time"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        if result.get("end_time"):
            try:
                end_time = datetime.fromisoformat(
                    result["end_time"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        # Validate: end_time > start_time
        if start_time and end_time and end_time <= start_time:
            # Swap if reversed
            start_time, end_time = end_time, start_time

        return {
            "start_time": start_time,
            "end_time": end_time,
            "confidence": result.get("confidence", 0.5),
            "explicit": result.get("explicit", False),
        }


# Module-level singleton
time_extractor = TimeRangeExtractor()

__all__ = ["TimeRangeExtractor", "time_extractor"]

