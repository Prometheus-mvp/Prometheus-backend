"""User model."""

import uuid

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    """User model (references Supabase Auth)."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=True)
    display_name = Column(Text, nullable=True)
    timezone = Column(Text, nullable=False, server_default="UTC")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    linked_accounts = relationship(
        "LinkedAccount", back_populates="user", cascade="all, delete-orphan"
    )
    oauth_tokens = relationship(
        "OAuthToken", back_populates="user", cascade="all, delete-orphan"
    )
    threads = relationship(
        "Thread", back_populates="user", cascade="all, delete-orphan"
    )
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    entities = relationship(
        "Entity", back_populates="user", cascade="all, delete-orphan"
    )
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    calendar_events = relationship(
        "CalendarEvent", back_populates="user", cascade="all, delete-orphan"
    )
    summaries = relationship(
        "Summary", back_populates="user", cascade="all, delete-orphan"
    )
    proposals = relationship(
        "Proposal", back_populates="user", cascade="all, delete-orphan"
    )
    drafts = relationship("Draft", back_populates="user", cascade="all, delete-orphan")
    embeddings = relationship(
        "Embedding", back_populates="user", cascade="all, delete-orphan"
    )
