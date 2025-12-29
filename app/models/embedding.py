"""Embedding model with pgvector."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Embedding(Base):
    """Embedding model with pgvector support."""

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    object_type = Column(
        String(50), nullable=False
    )  # event | note | thread | draft | entity
    object_id = Column(UUID(as_uuid=True), nullable=False)
    chunk_index = Column(Integer, nullable=False, server_default="0")
    embedding_model = Column(String(100), nullable=False)
    embedding_dim = Column(Integer, nullable=False)
    distance_metric = Column(String(50), nullable=False, server_default="cosine")
    embedding = Column(Vector(1536), nullable=False)
    content_hash = Column(String(255), nullable=False)
    metadata = Column(JSONB, nullable=False, server_default="{}")
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
            "user_id",
            "object_type",
            "object_id",
            "chunk_index",
            "embedding_model",
            name="uq_embeddings_user_object_chunk_model",
        ),
        Index("idx_embeddings_user_object_type", "user_id", "object_type"),
        Index("idx_embeddings_user_content_hash", "user_id", "content_hash"),
    )

    # Relationships (polymorphic based on object_type)
    user = relationship("User", back_populates="embeddings")
    event = relationship(
        "Event",
        back_populates="embeddings",
        foreign_keys="Event.id",
        primaryjoin="and_(Embedding.object_type=='event', Embedding.object_id==Event.id)",
        viewonly=True,
    )
    note = relationship(
        "Note",
        back_populates="embeddings",
        foreign_keys="Note.id",
        primaryjoin="and_(Embedding.object_type=='note', Embedding.object_id==Note.id)",
        viewonly=True,
    )
    draft = relationship(
        "Draft",
        back_populates="embeddings",
        foreign_keys="Draft.id",
        primaryjoin="and_(Embedding.object_type=='draft', Embedding.object_id==Draft.id)",
        viewonly=True,
    )
    entity = relationship(
        "Entity",
        back_populates="embeddings",
        foreign_keys="Entity.id",
        primaryjoin="and_(Embedding.object_type=='entity', Embedding.object_id==Entity.id)",
        viewonly=True,
    )
