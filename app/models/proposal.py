"""Proposal model."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Proposal(Base):
    """Proposal model."""

    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    content_json = Column(JSONB, nullable=False)
    source_refs = Column(JSONB, nullable=False, server_default="[]")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Constraints and Indexes
    __table_args__ = (
        Index("idx_proposals_user_window", "user_id", "window_start", "window_end"),
        CheckConstraint(
            "window_end > window_start",
            name="ck_proposals_valid_window",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="proposals")
