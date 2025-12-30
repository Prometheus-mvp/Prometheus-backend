"""Prompt Pydantic schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PromptRequest(BaseModel):
    """Prompt request schema."""

    prompt: str
    context: Optional[Dict[str, Any]] = {}


class PromptResponse(BaseModel):
    """Prompt response schema."""

    intent: str  # summarize | task
    response: Dict[str, Any]


