"""Tests for AgentOrchestrator."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


class TestAgentOrchestrator:
    """Test AgentOrchestrator functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def orchestrator(self, mock_session):
        """Create an orchestrator instance."""
        from app.agents.orchestrator import AgentOrchestrator

        return AgentOrchestrator(session=mock_session, user_id="test-user-id")

    @pytest.mark.asyncio
    async def test_execute_agent_persists_result(self, orchestrator, mock_session):
        """Test that execute_agent persists execution result."""

        async def mock_agent_method():
            return {"result": "test"}

        result = await orchestrator.execute_agent(
            "test_agent",
            mock_agent_method,
            intent="test",
            input_prompt="test prompt",
            input_params={"key": "value"},
        )

        assert result == {"result": "test"}
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_caches_result(self, orchestrator):
        """Test that execute_agent caches execution for deduplication."""
        call_count = 0

        async def mock_agent_method():
            nonlocal call_count
            call_count += 1
            return {"result": "test"}

        # First call
        result1 = await orchestrator.execute_agent(
            "test_agent",
            mock_agent_method,
            intent="test",
            input_prompt="test prompt",
            input_params={},
        )

        # Second call with same parameters should hit cache
        result2 = await orchestrator.execute_agent(
            "test_agent",
            mock_agent_method,
            intent="test",
            input_prompt="test prompt",
            input_params={},
        )

        assert result1 == result2
        assert call_count == 1  # Should only be called once

    @pytest.mark.asyncio
    async def test_get_agent_result_returns_previous_execution(
        self, orchestrator, mock_session
    ):
        """Test that get_agent_result returns previous execution."""
        from app.models import AgentExecution

        # Mock the query result
        mock_execution = MagicMock(spec=AgentExecution)
        mock_execution.output_result = {"overview": "test summary"}

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_execution]
        mock_session.execute.return_value = mock_result

        result = await orchestrator.get_agent_result("summarize")

        assert result == {"overview": "test summary"}

    @pytest.mark.asyncio
    async def test_get_agent_result_returns_none_if_not_found(
        self, orchestrator, mock_session
    ):
        """Test that get_agent_result returns None if no execution found."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await orchestrator.get_agent_result("summarize")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_recent_executions(self, orchestrator, mock_session):
        """Test that get_recent_executions returns multiple executions."""
        from app.models import AgentExecution

        # Mock executions
        mock_exec1 = MagicMock(spec=AgentExecution)
        mock_exec1.agent_name = "summarize"
        mock_exec1.intent = "summarize"
        mock_exec1.input_prompt = "test"
        mock_exec1.output_result = {"overview": "summary 1"}
        mock_exec1.created_at = datetime.now(timezone.utc)

        mock_exec2 = MagicMock(spec=AgentExecution)
        mock_exec2.agent_name = "query"
        mock_exec2.intent = "query"
        mock_exec2.input_prompt = "test"
        mock_exec2.output_result = {"answer": "answer 1"}
        mock_exec2.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_exec1, mock_exec2]
        mock_session.execute.return_value = mock_result

        results = await orchestrator.get_recent_executions(hours=24)

        assert len(results) == 2

    def test_session_id_is_unique_per_orchestrator(self, mock_session):
        """Test that each orchestrator gets a unique session ID."""
        from app.agents.orchestrator import AgentOrchestrator

        orch1 = AgentOrchestrator(session=mock_session, user_id="user1")
        orch2 = AgentOrchestrator(session=mock_session, user_id="user1")

        assert orch1.session_id != orch2.session_id


class TestInterAgentCommunication:
    """Test inter-agent communication via orchestrator."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_query_agent_can_call_summarize_agent(self, mock_session):
        """Test that QueryAgent can call SummarizeAgent through orchestrator."""
        from app.agents.orchestrator import AgentOrchestrator
        from app.models import AgentExecution

        orchestrator = AgentOrchestrator(session=mock_session, user_id="test-user-id")

        # Mock previous summarize execution
        mock_execution = MagicMock(spec=AgentExecution)
        mock_execution.output_result = {"overview": "Previous summary"}

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_execution]
        mock_session.execute.return_value = mock_result

        # QueryAgent gets SummarizeAgent result
        summary_result = await orchestrator.get_agent_result(
            "summarize", time_window_hours=24
        )

        assert summary_result == {"overview": "Previous summary"}
