"""Tests for push-based QueryAgent."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestQueryAgent:
    """Test QueryAgent push-based functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store."""
        store = MagicMock()
        store.search = AsyncMock(return_value=[])
        store.store_embedding = AsyncMock()
        return store

    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        service = MagicMock()
        service.embed_text = AsyncMock(return_value=[[0.1] * 1536])
        service.embed_and_store = AsyncMock(return_value=1)
        return service

    @pytest.mark.asyncio
    async def test_build_context_bank_calls_ingestion(
        self, mock_session, mock_vector_store, mock_embedding_service
    ):
        """Test that build_context_bank calls ingestion job."""
        from app.agents.query_graph import QueryAgent

        with patch(
            "app.agents.query_graph.ingest_events_for_user",
            new_callable=AsyncMock,
        ) as mock_ingest:
            mock_ingest.return_value = 5

            agent = QueryAgent(
                vector_store=mock_vector_store,
                embedding_service=mock_embedding_service,
            )
            result = await agent.build_context_bank(
                mock_session,
                user_id="test-user-id",
                time_window_hours=24,
            )

            mock_ingest.assert_called_once_with(mock_session, "test-user-id")
            assert result["events_processed"] == 5

    @pytest.mark.asyncio
    async def test_fine_grained_search_uses_hybrid_ranking(
        self, mock_session, mock_vector_store, mock_embedding_service
    ):
        """Test that fine_grained_search uses hybrid ranking."""
        from app.agents.query_graph import QueryAgent
        from app.services.vector import VectorRecord

        # Mock search results with recency scores
        mock_vector_store.search.return_value = [
            VectorRecord(
                id="emb-1",
                object_type="event",
                object_id="evt-1",
                chunk_index=0,
                score=0.1,
                metadata={"source": "slack"},
                recency_score=0.9,
                semantic_score=0.9,
                final_score=0.9,
            )
        ]

        agent = QueryAgent(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )
        result = await agent.fine_grained_search(
            mock_session,
            user_id="test-user-id",
            query="test query",
            sources=["slack"],
        )

        assert len(result["results"]) == 1
        assert result["results"][0]["recency_score"] == 0.9
        assert result["results"][0]["semantic_score"] == 0.9

    @pytest.mark.asyncio
    async def test_answer_query_with_context_uses_context_bank(
        self, mock_session, mock_vector_store, mock_embedding_service
    ):
        """Test that answer_query_with_context uses context bank."""
        from app.agents.query_graph import QueryAgent
        from app.services.vector import VectorRecord

        # Mock search results
        mock_vector_store.search.return_value = [
            VectorRecord(
                id="emb-1",
                object_type="event",
                object_id="evt-1",
                chunk_index=0,
                score=0.1,
                metadata={"source": "slack"},
                recency_score=0.8,
                semantic_score=0.9,
                final_score=0.85,
            )
        ]

        agent = QueryAgent(
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )

        with patch.object(agent, "complete_json", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {
                "answer": "Test answer",
                "confidence": 0.9,
                "citations": ["evt-1"],
            }

            now = datetime.now(timezone.utc)
            result = await agent.answer_query_with_context(
                mock_session,
                user_id="test-user-id",
                prompt="What did John say?",
                sources=["slack"],
                time_start=now - timedelta(hours=2),
                time_end=now,
            )

            assert result["answer"] == "Test answer"
            assert result["confidence"] == 0.9


class TestQueryAgentBackgroundJob:
    """Test QueryAgent background job."""

    @pytest.mark.asyncio
    async def test_background_job_calls_build_context_bank(self):
        """Test that background job calls build_context_bank."""
        with patch(
            "app.jobs.query_agent.AsyncSessionLocal"
        ) as mock_session_local:
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.commit = AsyncMock()
            mock_session_local.return_value = mock_session

            with patch(
                "app.jobs.query_agent.QueryAgent"
            ) as mock_query_agent_class:
                mock_agent = MagicMock()
                mock_agent.build_context_bank = AsyncMock(
                    return_value={"events_processed": 10}
                )
                mock_query_agent_class.return_value = mock_agent

                from app.jobs.query_agent import run_query_agent_context_bank

                result = await run_query_agent_context_bank("test-user-id")

                mock_agent.build_context_bank.assert_called_once()
                assert result["events_processed"] == 10

