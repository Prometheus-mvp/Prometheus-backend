"""AgentExecution model for persisting agent results."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AgentExecution(Base):
    """Stores agent execution results for inter-agent context sharing."""

    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True), nullable=False, index=True
    )  # Groups related executions within a request
    agent_name = Column(
        String(100), nullable=False
    )  # "summarize", "task", "query", "source_extractor", etc.
    intent = Column(String(50), nullable=True)  # summarize | task | query
    input_prompt = Column(Text, nullable=False)
    input_params = Column(
        JSONB, nullable=False, server_default="{}"
    )  # sources, time_range, etc.
    output_result = Column(JSONB, nullable=False)  # Agent's output
    execution_metadata = Column(
        JSONB, nullable=False, server_default="{}"
    )  # timing, tokens, etc.
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Indexes for efficient retrieval
    __table_args__ = (
        Index("idx_agent_executions_user_session", "user_id", "session_id"),
        Index(
            "idx_agent_executions_user_agent_created",
            "user_id",
            "agent_name",
            "created_at",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="agent_executions")

