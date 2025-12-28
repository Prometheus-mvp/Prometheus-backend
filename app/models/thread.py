"""Thread model for conversation threads."""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Thread(Base):
    """Thread model for conversation threads."""

    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(Text, nullable=False)  # slack | telegram | outlook
    external_id = Column(Text, nullable=False)
    subject = Column(Text, nullable=True)
    participants = Column(JSONB, nullable=False, server_default="[]")
    content_preview = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=False, server_default="")
    last_event_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "source", "external_id", name="uq_threads_user_source_external"),
        Index("idx_threads_user_source_last_event", "user_id", "source", "last_event_at"),
    )

    # Relationships
    user = relationship("User", back_populates="threads")
    events = relationship("Event", back_populates="thread")

