"""OAuthToken model."""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class OAuthToken(Base):
    """OAuth token model with encrypted storage."""

    __tablename__ = "oauth_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    linked_account_id = Column(UUID(as_uuid=True), ForeignKey("linked_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    token_type = Column(Text, nullable=False)  # bearer | bot
    scopes = Column(Text, nullable=True)
    access_token_enc = Column(Text, nullable=False)  # AES-256-GCM encrypted
    refresh_token_enc = Column(Text, nullable=True)  # AES-256-GCM encrypted
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    token_fingerprint = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_oauth_tokens_user_linked_account", "user_id", "linked_account_id"),
    )

    # Relationships
    user = relationship("User", back_populates="oauth_tokens")
    linked_account = relationship("LinkedAccount", back_populates="oauth_tokens")

