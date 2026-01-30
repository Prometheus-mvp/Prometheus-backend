"""Agent Orchestrator for managing inter-agent communication and context."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AgentExecution

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates agent execution and manages inter-agent communication.

    All agent calls should go through the orchestrator to:
    - Persist execution results for context sharing
    - Enable inter-agent communication
    - Manage session isolation
    - Cache results for deduplication
    """

    def __init__(self, session: AsyncSession, user_id: str) -> None:
        self.session = session
        self.user_id = user_id
        self.session_id = uuid.uuid4()  # New session for each request
        self.execution_cache: Dict[str, AgentExecution] = {}  # In-memory cache

    async def execute_agent(
        self,
        agent_name: str,
        agent_method: Callable,
        *args,
        intent: Optional[str] = None,
        input_prompt: str,
        input_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute an agent and persist the result.

        All agent calls must go through orchestrator for:
        - Execution persistence
        - Result caching
        - Inter-agent context sharing
        """
        input_params = input_params or {}

        # Check cache first
        cache_key = self._make_cache_key(agent_name, input_prompt, input_params)
        if cache_key in self.execution_cache:
            logger.debug(
                "Cache hit for agent execution",
                extra={"agent_name": agent_name, "cache_key": cache_key[:16]},
            )
            return self.execution_cache[cache_key].output_result

        # Execute agent
        start_time = datetime.now(timezone.utc)
        try:
            result = await agent_method(*args, **kwargs)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        except Exception as exc:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(
                "Agent execution failed",
                extra={
                    "agent_name": agent_name,
                    "execution_time": execution_time,
                    "error": str(exc),
                },
            )
            raise

        # Persist execution result
        execution = AgentExecution(
            user_id=self.user_id,
            session_id=self.session_id,
            agent_name=agent_name,
            intent=intent,
            input_prompt=input_prompt,
            input_params=input_params,
            output_result=result,
            execution_metadata={
                "execution_time_seconds": execution_time,
                "timestamp": start_time.isoformat(),
            },
        )
        self.session.add(execution)
        await self.session.flush()  # Get ID without committing

        # Cache for current session
        self.execution_cache[cache_key] = execution

        logger.debug(
            "Agent execution persisted",
            extra={
                "agent_name": agent_name,
                "session_id": str(self.session_id),
                "execution_time": execution_time,
            },
        )

        return result

    async def get_agent_result(
        self,
        agent_name: str,
        time_window_hours: Optional[int] = None,
        session_id: Optional[UUID] = None,
        limit: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve previous agent execution results for use as context.

        Agents can call this to get outputs from other agents.
        Used for inter-agent communication.
        """
        query = (
            select(AgentExecution)
            .where(AgentExecution.user_id == self.user_id)
            .where(AgentExecution.agent_name == agent_name)
            .order_by(AgentExecution.created_at.desc())
        )

        if session_id:
            query = query.where(AgentExecution.session_id == session_id)

        if time_window_hours:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
            query = query.where(AgentExecution.created_at >= cutoff)

        result = await self.session.execute(query.limit(limit))
        executions = result.scalars().all()

        if executions:
            return executions[0].output_result
        return None

    async def get_recent_executions(
        self,
        agent_names: Optional[List[str]] = None,
        hours: int = 24,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get recent executions from multiple agents for context.

        Useful for building comprehensive context from multiple agent outputs.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(AgentExecution)
            .where(AgentExecution.user_id == self.user_id)
            .where(AgentExecution.created_at >= cutoff)
            .order_by(AgentExecution.created_at.desc())
            .limit(limit)
        )

        if agent_names:
            query = query.where(AgentExecution.agent_name.in_(agent_names))

        result = await self.session.execute(query)
        executions = result.scalars().all()

        return [
            {
                "agent_name": ex.agent_name,
                "intent": ex.intent,
                "input_prompt": ex.input_prompt,
                "output_result": ex.output_result,
                "created_at": ex.created_at.isoformat(),
            }
            for ex in executions
        ]

    def _make_cache_key(
        self, agent_name: str, prompt: str, params: Dict[str, Any]
    ) -> str:
        """Generate cache key for execution deduplication."""
        # Sort params for consistent key generation
        sorted_params = sorted(params.items()) if params else []
        key_str = f"{agent_name}:{prompt}:{sorted_params}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    @property
    def current_session_id(self) -> UUID:
        """Get the current session ID."""
        return self.session_id


__all__ = ["AgentOrchestrator"]
