"""Draft model."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Draft(Base):
    """Draft model."""

    __tablename__ = "drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = Column(
        String(50), nullable=False
    )  # slack_reply | telegram_reply | outlook_reply | note
    content_json = Column(JSONB, nullable=False)
    content_hash = Column(String(255), nullable=False, server_default="")
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
        Index("idx_drafts_user_kind_created", "user_id", "kind", "created_at"),
        CheckConstraint(
            "kind IN ('slack_reply', 'telegram_reply', 'outlook_reply', 'note')",
            name="ck_drafts_kind",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="drafts")
    embeddings = relationship(
        "Embedding",
        primaryjoin="and_(Embedding.object_type=='draft', Embedding.object_id==Draft.id)",
        foreign_keys="Embedding.object_id",
        viewonly=True,  # Required for polymorphic relationships
    )
