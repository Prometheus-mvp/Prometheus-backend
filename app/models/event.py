"""Event model for events from connectors."""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Event(Base):
    """Event model for events from connectors."""

    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source = Column(Text, nullable=False)  # slack | telegram | outlook | calendar
    source_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("linked_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    external_id = Column(Text, nullable=False)
    thread_id = Column(
        UUID(as_uuid=True), ForeignKey("threads.id", ondelete="SET NULL"), nullable=True
    )
    event_type = Column(
        Text, nullable=False
    )  # message | reaction | mention | file | email | calendar_created etc.
    title = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    text_for_embedding = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=False, server_default="")
    importance_score = Column(SmallInteger, nullable=False, server_default="0")
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    raw = Column(JSONB, nullable=False, server_default="{}")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "source", "external_id", name="uq_events_user_source_external"
        ),
        Index("idx_events_user_source_occurred", "user_id", "source", "occurred_at"),
        Index("idx_events_user_expires", "user_id", "expires_at"),
        Index("idx_events_user_deleted", "user_id", "deleted_at"),
    )

    # Relationships
    user = relationship("User", back_populates="events")
    source_account = relationship(
        "LinkedAccount", back_populates="events", foreign_keys=[source_account_id]
    )
    thread = relationship("Thread", back_populates="events")
    tasks = relationship(
        "Task", back_populates="source_event", foreign_keys="Task.source_event_id"
    )
    embeddings = relationship(
        "Embedding",
        back_populates="event",
        foreign_keys="Embedding.object_id",
        primaryjoin="and_(Embedding.object_type=='event', Embedding.object_id==Event.id)",
    )
