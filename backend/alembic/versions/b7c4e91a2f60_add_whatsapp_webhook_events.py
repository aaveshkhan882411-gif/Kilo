"""add WhatsApp inbound webhook events

Revision ID: b7c4e91a2f60
Revises: d436a9da00e0
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c4e91a2f60"
down_revision: Union[str, None] = "d436a9da00e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_webhook_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=False),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("phone_number_id", sa.String(length=255), nullable=False),
        sa.Column("sender_phone", sa.String(length=50), nullable=False),
        sa.Column(
            "message_type",
            sa.String(length=50),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("message_body", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="received",
        ),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id"),
    )
    op.create_index(
        "ix_whatsapp_webhook_events_org_id",
        "whatsapp_webhook_events",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        "ix_whatsapp_webhook_events_status",
        "whatsapp_webhook_events",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_whatsapp_webhook_events_status",
        table_name="whatsapp_webhook_events",
    )
    op.drop_index(
        "ix_whatsapp_webhook_events_org_id",
        table_name="whatsapp_webhook_events",
    )
    op.drop_table("whatsapp_webhook_events")
