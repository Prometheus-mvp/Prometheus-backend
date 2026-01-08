"""Prompt Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PromptRequest(BaseModel):
    """Prompt request schema."""

    prompt: str
    context: Optional[Dict[str, Any]] = {}


class PromptClarificationRequest(BaseModel):
    """Response when prompt needs clarification."""

    missing_fields: List[str]  # ["sources", "time_range"]
    message: str
    prompt: str  # Original prompt


class TimeRange(BaseModel):
    """Extracted time range."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    confidence: float  # 0.0-1.0


class PromptResponse(BaseModel):
    """Prompt response schema."""

    intent: str  # summarize | task | query
    response: Dict[str, Any]
    clarification_needed: Optional[PromptClarificationRequest] = None
    execution_id: Optional[str] = None  # Link to agent execution record

