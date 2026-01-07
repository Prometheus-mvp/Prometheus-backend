"""Add CHECK constraints and standardize content_hash

Revision ID: 003_add_check_constraints_and_standardize
Revises: 001_initial_schema
Create Date: 2025-01-15 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "003_add_check_constraints_and_standardize"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Standardize content_hash columns from Text to String(255)
    op.alter_column("events", "content_hash", type_=sa.String(255), existing_type=sa.Text())
    op.alter_column("notes", "content_hash", type_=sa.String(255), existing_type=sa.Text())
    op.alter_column("threads", "content_hash", type_=sa.String(255), existing_type=sa.Text())

    # Add CHECK constraints for Task model
    op.create_check_constraint(
        "ck_tasks_status",
        "tasks",
        "status IN ('open', 'done', 'snoozed')",
    )
    op.create_check_constraint(
        "ck_tasks_priority",
        "tasks",
        "priority IN ('low', 'medium', 'high')",
    )

    # Add CHECK constraints for Event model
    op.create_check_constraint(
        "ck_events_source",
        "events",
        "source IN ('slack', 'telegram', 'outlook', 'calendar')",
    )
    op.create_check_constraint(
        "ck_events_event_type",
        "events",
        "event_type IN ('message', 'reaction', 'mention', 'file', 'email', 'calendar_created', 'calendar_updated', 'calendar_deleted')",
    )

    # Add CHECK constraints for Entity model
    op.create_check_constraint(
        "ck_entities_kind",
        "entities",
        "kind IN ('person', 'org', 'project', 'topic')",
    )

    # Add CHECK constraints for Draft model
    op.create_check_constraint(
        "ck_drafts_kind",
        "drafts",
        "kind IN ('slack_reply', 'telegram_reply', 'outlook_reply', 'note')",
    )

    # Add CHECK constraints for LinkedAccount model
    op.create_check_constraint(
        "ck_linked_accounts_provider",
        "linked_accounts",
        "provider IN ('slack', 'telegram', 'outlook')",
    )
    op.create_check_constraint(
        "ck_linked_accounts_status",
        "linked_accounts",
        "status IN ('active', 'revoked', 'error')",
    )

    # Add CHECK constraints for OAuthToken model
    op.create_check_constraint(
        "ck_oauth_tokens_token_type",
        "oauth_tokens",
        "token_type IN ('bearer', 'bot')",
    )

    # Add CHECK constraints for Thread model
    op.create_check_constraint(
        "ck_threads_source",
        "threads",
        "source IN ('slack', 'telegram', 'outlook')",
    )

    # Add window validation constraints
    op.create_check_constraint(
        "ck_summaries_valid_window",
        "summaries",
        "window_end > window_start",
    )
    op.create_check_constraint(
        "ck_proposals_valid_window",
        "proposals",
        "window_end > window_start",
    )
    op.create_check_constraint(
        "ck_calendar_events_valid_time_range",
        "calendar_events",
        "end_at > start_at",
    )


def downgrade() -> None:
    # Drop CHECK constraints
    op.drop_constraint("ck_calendar_events_valid_time_range", "calendar_events", type_="check")
    op.drop_constraint("ck_proposals_valid_window", "proposals", type_="check")
    op.drop_constraint("ck_summaries_valid_window", "summaries", type_="check")
    op.drop_constraint("ck_threads_source", "threads", type_="check")
    op.drop_constraint("ck_oauth_tokens_token_type", "oauth_tokens", type_="check")
    op.drop_constraint("ck_linked_accounts_status", "linked_accounts", type_="check")
    op.drop_constraint("ck_linked_accounts_provider", "linked_accounts", type_="check")
    op.drop_constraint("ck_drafts_kind", "drafts", type_="check")
    op.drop_constraint("ck_entities_kind", "entities", type_="check")
    op.drop_constraint("ck_events_event_type", "events", type_="check")
    op.drop_constraint("ck_events_source", "events", type_="check")
    op.drop_constraint("ck_tasks_priority", "tasks", type_="check")
    op.drop_constraint("ck_tasks_status", "tasks", type_="check")

    # Revert content_hash columns back to Text
    op.alter_column("threads", "content_hash", type_=sa.Text(), existing_type=sa.String(255))
    op.alter_column("notes", "content_hash", type_=sa.Text(), existing_type=sa.String(255))
    op.alter_column("events", "content_hash", type_=sa.Text(), existing_type=sa.String(255))

