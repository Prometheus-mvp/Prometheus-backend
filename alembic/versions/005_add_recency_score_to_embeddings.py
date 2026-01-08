"""Add recency_score to embeddings.

Revision ID: 005
Revises: 004
Create Date: 2026-01-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add recency_score column to embeddings table
    op.add_column(
        "embeddings",
        sa.Column("recency_score", sa.Float(), nullable=True),
    )
    # Create index for efficient recency-based queries
    op.create_index(
        "idx_embeddings_recency_score",
        "embeddings",
        ["recency_score"],
    )


def downgrade() -> None:
    op.drop_index("idx_embeddings_recency_score", table_name="embeddings")
    op.drop_column("embeddings", "recency_score")

