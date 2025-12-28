"""Note model."""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Note(Base):
    """Note model."""

    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False, server_default="")
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_notes_user_updated", "user_id", "updated_at"),
    )

    # Relationships
    user = relationship("User", back_populates="notes")
    embeddings = relationship("Embedding", back_populates="note", foreign_keys="Embedding.object_id", primaryjoin="and_(Embedding.object_type=='note', Embedding.object_id==Note.id)")

