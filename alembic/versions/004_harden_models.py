"""Harden model constraints and defaults.

Revision ID: 004_harden_models
Revises: 003_add_check_constraints_and_standardize
Create Date: 2026-01-07 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "004_harden_models"
down_revision = "003_add_check_constraints_and_standardize"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enforce temporal ordering on events
    op.create_check_constraint(
        "ck_events_time_range",
        "events",
        "expires_at > occurred_at",
    )

    # Tighten embedding integrity
    op.create_check_constraint(
        "ck_embeddings_object_type",
        "embeddings",
        "object_type IN ('event', 'note', 'thread', 'draft', 'entity')",
    )
    op.create_check_constraint(
        "ck_embeddings_dim_matches_vector",
        "embeddings",
        "embedding_dim = 1536",
    )

    # Default task status to open
    op.alter_column(
        "tasks",
        "status",
        server_default=sa.text("'open'"),
        existing_type=sa.Text(),
    )

    # Enforce unique user emails
    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.alter_column(
        "tasks",
        "status",
        server_default=None,
        existing_type=sa.Text(),
    )
    op.drop_constraint("ck_embeddings_dim_matches_vector", "embeddings", type_="check")
    op.drop_constraint("ck_embeddings_object_type", "embeddings", type_="check")
    op.drop_constraint("ck_events_time_range", "events", type_="check")
