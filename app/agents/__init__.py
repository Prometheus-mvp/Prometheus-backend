"""Agent modules for the Prometheus backend.

Agent types:
- QueryAgent (Push-based): Proactively builds context bank
- SummarizeAgent (Pull-based): Only executes on explicit user request
- TaskAgent (Neither): Performs tasks, not push or pull based
"""

from app.agents.base import AgentBase
from app.agents.orchestrator import AgentOrchestrator
from app.agents.prompt_router import PromptRouterAgent, prompt_router
from app.agents.query_graph import QueryAgent, query_agent
from app.agents.source_extractor import SourceExtractor, source_extractor
from app.agents.summarize_graph import SummarizeAgent, summarize_agent
from app.agents.task_graph import TaskAgent, task_agent
from app.agents.time_extractor import TimeRangeExtractor, time_extractor

__all__ = [
    # Base
    "AgentBase",
    # Orchestrator
    "AgentOrchestrator",
    # Agents
    "PromptRouterAgent",
    "prompt_router",
    "QueryAgent",
    "query_agent",
    "SummarizeAgent",
    "summarize_agent",
    "TaskAgent",
    "task_agent",
    # Extractors
    "SourceExtractor",
    "source_extractor",
    "TimeRangeExtractor",
    "time_extractor",
]
