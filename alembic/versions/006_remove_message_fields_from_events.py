"""Remove message fields from events.

Messages are not stored - only used for generating embeddings.

Revision ID: 006
Revises: 005
Create Date: 2026-01-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove message content fields - messages only used for embeddings, not stored
    op.drop_column("events", "body")
    op.drop_column("events", "text_for_embedding")


def downgrade() -> None:
    # Re-add the columns if needed to rollback
    op.add_column(
        "events",
        sa.Column("text_for_embedding", sa.Text(), nullable=True),
    )
    op.add_column(
        "events",
        sa.Column("body", sa.Text(), nullable=True),
    )

