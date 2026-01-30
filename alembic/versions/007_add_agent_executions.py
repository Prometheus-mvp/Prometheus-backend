"""Add agent_executions table.

Stores agent execution results for inter-agent context sharing.

Revision ID: 007
Revises: 006
Create Date: 2026-01-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_executions",
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
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("intent", sa.String(50), nullable=True),
        sa.Column("input_prompt", sa.Text(), nullable=False),
        sa.Column(
            "input_params", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column("output_result", postgresql.JSONB(), nullable=False),
        sa.Column(
            "execution_metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Create indexes
    op.create_index(
        "idx_agent_executions_user_id",
        "agent_executions",
        ["user_id"],
    )
    op.create_index(
        "idx_agent_executions_session_id",
        "agent_executions",
        ["session_id"],
    )
    op.create_index(
        "idx_agent_executions_user_session",
        "agent_executions",
        ["user_id", "session_id"],
    )
    op.create_index(
        "idx_agent_executions_user_agent_created",
        "agent_executions",
        ["user_id", "agent_name", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_agent_executions_user_agent_created", table_name="agent_executions"
    )
    op.drop_index("idx_agent_executions_user_session", table_name="agent_executions")
    op.drop_index("idx_agent_executions_session_id", table_name="agent_executions")
    op.drop_index("idx_agent_executions_user_id", table_name="agent_executions")
    op.drop_table("agent_executions")
