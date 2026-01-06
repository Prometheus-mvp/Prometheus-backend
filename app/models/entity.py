"""Entity model for person/org/project/topic."""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Entity(Base):
    """Entity model for person/org/project/topic."""

    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = Column(Text, nullable=False)  # person | org | project | topic
    name = Column(Text, nullable=False)
    aliases = Column(JSONB, nullable=False, server_default="[]")
    meta = Column("metadata", JSONB, nullable=False, server_default="{}")
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
        Index("idx_entities_user_kind_name", "user_id", "kind", "name"),
        CheckConstraint(
            "kind IN ('person', 'org', 'project', 'topic')",
            name="ck_entities_kind",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="entities")
    embeddings = relationship(
        "Embedding",
        back_populates="entity",
        foreign_keys="Embedding.object_id",
        primaryjoin="and_(Embedding.object_type=='entity', Embedding.object_id==Entity.id)",
    )
