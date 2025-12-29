"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # Users (reference Supabase Auth)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="UTC"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Linked accounts
    op.create_table(
        "linked_accounts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.Text(), nullable=False),  # slack | telegram | outlook
        sa.Column("provider_account_id", sa.Text(), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.Text(), nullable=False, server_default="active"
        ),  # active | revoked | error
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "provider_account_id",
            name="uq_linked_accounts_user_provider_account",
        ),
    )
    op.create_index(
        "idx_linked_accounts_user_provider", "linked_accounts", ["user_id", "provider"]
    )
    op.create_index("idx_linked_accounts_user_id", "linked_accounts", ["user_id"])

    # OAuth tokens
    op.create_table(
        "oauth_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "linked_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("linked_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_type", sa.Text(), nullable=False),  # bearer | bot
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column(
            "access_token_enc", sa.Text(), nullable=False
        ),  # AES-256-GCM encrypted
        sa.Column(
            "refresh_token_enc", sa.Text(), nullable=True
        ),  # AES-256-GCM encrypted
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_refreshed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("token_fingerprint", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_oauth_tokens_user_linked_account",
        "oauth_tokens",
        ["user_id", "linked_account_id"],
    )
    op.create_index("idx_oauth_tokens_user_id", "oauth_tokens", ["user_id"])
    op.create_index(
        "idx_oauth_tokens_linked_account_id", "oauth_tokens", ["linked_account_id"]
    )

    # Threads
    op.create_table(
        "threads",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.Text(), nullable=False),  # slack | telegram | outlook
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column(
            "participants", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("content_preview", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=False, server_default=""),
        sa.Column("last_event_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id", "source", "external_id", name="uq_threads_user_source_external"
        ),
    )
    op.create_index(
        "idx_threads_user_source_last_event",
        "threads",
        ["user_id", "source", "last_event_at"],
    )
    op.create_index("idx_threads_user_id", "threads", ["user_id"])

    # Events
    op.create_table(
        "events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source", sa.Text(), nullable=False
        ),  # slack | telegram | outlook | calendar
        sa.Column(
            "source_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("linked_accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column(
            "thread_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("threads.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "event_type", sa.Text(), nullable=False
        ),  # message | reaction | mention | file | email | calendar_created etc.
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("text_for_embedding", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "importance_score", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("raw", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id", "source", "external_id", name="uq_events_user_source_external"
        ),
    )
    op.create_index(
        "idx_events_user_source_occurred",
        "events",
        ["user_id", "source", "occurred_at"],
    )
    op.create_index("idx_events_user_expires", "events", ["user_id", "expires_at"])
    op.create_index("idx_events_user_deleted", "events", ["user_id", "deleted_at"])
    op.create_index("idx_events_user_id", "events", ["user_id"])

    # Entities
    op.create_table(
        "entities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.Text(), nullable=False),  # person | org | project | topic
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("aliases", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_entities_user_kind_name", "entities", ["user_id", "kind", "name"]
    )
    op.create_index("idx_entities_user_id", "entities", ["user_id"])

    # Notes
    op.create_table(
        "notes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=False, server_default=""),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_notes_user_updated", "notes", ["user_id", "updated_at"])
    op.create_index("idx_notes_user_id", "notes", ["user_id"])

    # Tasks
    op.create_table(
        "tasks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.Text(), nullable=False),  # open | done | snoozed
        sa.Column(
            "priority", sa.Text(), nullable=False, server_default="medium"
        ),  # low | medium | high
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("due_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "source_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("events.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source_refs", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_tasks_user_status_due", "tasks", ["user_id", "status", "due_at"]
    )
    op.create_index("idx_tasks_user_id", "tasks", ["user_id"])

    # Calendar events
    op.create_table(
        "calendar_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("end_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_calendar_events_user_start", "calendar_events", ["user_id", "start_at"]
    )
    op.create_index("idx_calendar_events_user_id", "calendar_events", ["user_id"])

    # Summaries
    op.create_table(
        "summaries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("window_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("window_end", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("content_json", postgresql.JSONB(), nullable=False),
        sa.Column(
            "source_refs", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_summaries_user_window",
        "summaries",
        ["user_id", "window_start", "window_end"],
    )
    op.create_index("idx_summaries_user_id", "summaries", ["user_id"])

    # Proposals
    op.create_table(
        "proposals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("window_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("window_end", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("content_json", postgresql.JSONB(), nullable=False),
        sa.Column(
            "source_refs", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_proposals_user_window",
        "proposals",
        ["user_id", "window_start", "window_end"],
    )
    op.create_index("idx_proposals_user_id", "proposals", ["user_id"])

    # Drafts
    op.create_table(
        "drafts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kind", sa.String(50), nullable=False
        ),  # slack_reply | telegram_reply | outlook_reply | note
        sa.Column("content_json", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "source_refs", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_drafts_user_kind_created", "drafts", ["user_id", "kind", "created_at"]
    )
    op.create_index("idx_drafts_user_id", "drafts", ["user_id"])

    # Embeddings (pgvector)
    op.create_table(
        "embeddings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "object_type", sa.String(50), nullable=False
        ),  # event | note | thread | draft | entity
        sa.Column("object_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding_model", sa.String(100), nullable=False),
        sa.Column("embedding_dim", sa.Integer(), nullable=False),
        sa.Column(
            "distance_metric", sa.String(50), nullable=False, server_default="cosine"
        ),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("content_hash", sa.String(255), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "object_type",
            "object_id",
            "chunk_index",
            "embedding_model",
            name="uq_embeddings_user_object_chunk_model",
        ),
    )
    op.create_index(
        "idx_embeddings_user_object_type", "embeddings", ["user_id", "object_type"]
    )
    op.create_index(
        "idx_embeddings_user_content_hash", "embeddings", ["user_id", "content_hash"]
    )
    op.create_index("idx_embeddings_user_id", "embeddings", ["user_id"])

    # Vector similarity index (HNSW for cosine similarity)
    op.execute(
        "CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_embeddings_vector")

    # Drop tables in reverse order
    op.drop_table("embeddings")
    op.drop_table("drafts")
    op.drop_table("proposals")
    op.drop_table("summaries")
    op.drop_table("calendar_events")
    op.drop_table("tasks")
    op.drop_table("notes")
    op.drop_table("entities")
    op.drop_table("events")
    op.drop_table("threads")
    op.drop_table("oauth_tokens")
    op.drop_table("linked_accounts")
    op.drop_table("users")

    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
