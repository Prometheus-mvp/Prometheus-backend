"""LinkedAccount model."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LinkedAccount(Base):
    """Linked account model for OAuth providers."""

    __tablename__ = "linked_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(Text, nullable=False)  # slack | telegram | outlook
    provider_account_id = Column(Text, nullable=False)
    scopes = Column(Text, nullable=True)
    status = Column(
        Text, nullable=False, server_default="active"
    )  # active | revoked | error
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
            "provider",
            "provider_account_id",
            name="uq_linked_accounts_user_provider_account",
        ),
        Index("idx_linked_accounts_user_provider", "user_id", "provider"),
    )

    # Relationships
    user = relationship("User", back_populates="linked_accounts")
    oauth_tokens = relationship(
        "OAuthToken", back_populates="linked_account", cascade="all, delete-orphan"
    )
    events = relationship(
        "Event", back_populates="source_account", foreign_keys="Event.source_account_id"
    )
