"""Task model."""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Task(Base):
    """Task model (what needs action)."""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Text, nullable=False)  # open | done | snoozed
    priority = Column(Text, nullable=False, server_default="medium")  # low | medium | high
    title = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    source_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    source_refs = Column(JSONB, nullable=False, server_default="[]")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_tasks_user_status_due", "user_id", "status", "due_at"),
    )

    # Relationships
    user = relationship("User", back_populates="tasks")
    source_event = relationship("Event", back_populates="tasks", foreign_keys=[source_event_id])

