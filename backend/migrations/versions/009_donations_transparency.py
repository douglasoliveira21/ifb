"""Donations and transparency tables

Revision ID: 009
Revises: 008
Create Date: 2026-08-05
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Donations
    op.create_table("donors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255)),
        sa.Column("email", sa.String(255), index=True),
        sa.Column("document_hash", sa.String(64), nullable=True),
        sa.Column("donor_type", sa.String(20), server_default="individual"),
        sa.Column("anonymous_publicly", sa.Boolean, server_default="false"),
        sa.Column("communication_consent", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("donation_campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("slug", sa.String(100), unique=True, index=True),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("goal_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("raised_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("donations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("donor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donors.id"), index=True),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donation_campaigns.id"), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="BRL"),
        sa.Column("frequency", sa.String(20), server_default="one_time"),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), server_default="created", index=True),
        sa.Column("public_display_authorized", sa.Boolean, server_default="false"),
        sa.Column("public_display_name", sa.String(255), nullable=True),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("idempotency_key", sa.String(255), unique=True, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("donation_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("donation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donations.id"), index=True),
        sa.Column("provider", sa.String(50)),
        sa.Column("external_payment_id", sa.String(255), index=True, nullable=True),
        sa.Column("external_checkout_id", sa.String(255), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2)),
        sa.Column("fee_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending", index=True),
        sa.Column("pix_qr_code", sa.Text, nullable=True),
        sa.Column("pix_copy_paste", sa.Text, nullable=True),
        sa.Column("checkout_url", sa.String(2048), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("donation_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("donation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donations.id"), index=True),
        sa.Column("provider", sa.String(50)),
        sa.Column("external_subscription_id", sa.String(255), index=True, nullable=True),
        sa.Column("amount", sa.Numeric(15, 2)),
        sa.Column("frequency", sa.String(20), server_default="monthly"),
        sa.Column("status", sa.String(50), server_default="pending", index=True),
        sa.Column("next_billing_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_payment_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("payment_webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("provider", sa.String(50), index=True),
        sa.Column("external_event_id", sa.String(255), index=True),
        sa.Column("event_type", sa.String(100)),
        sa.Column("payload_hash", sa.String(64)),
        sa.Column("signature_valid", sa.Boolean, server_default="false"),
        sa.Column("processing_status", sa.String(50), server_default="received"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_webhook_provider_event", "payment_webhook_events", ["provider", "external_event_id"], unique=True)
    op.create_table("donation_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("donation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donations.id"), index=True),
        sa.Column("receipt_number", sa.String(50), unique=True),
        sa.Column("amount", sa.Numeric(15, 2)),
        sa.Column("donor_name", sa.String(255)),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True)),
        sa.Column("file_path", sa.String(1024), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Transparency
    op.create_table("institutional_revenues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("date", sa.Date, index=True),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("description", sa.String(500)),
        sa.Column("gross_amount", sa.Numeric(15, 2)),
        sa.Column("fee_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_amount", sa.Numeric(15, 2)),
        sa.Column("source_type", sa.String(50)),
        sa.Column("donation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_url", sa.String(2048), nullable=True),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("institutional_expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("date", sa.Date, index=True),
        sa.Column("competence_date", sa.Date, nullable=True),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("supplier_name", sa.String(500), nullable=True),
        sa.Column("description", sa.String(500)),
        sa.Column("gross_amount", sa.Numeric(15, 2)),
        sa.Column("net_amount", sa.Numeric(15, 2)),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("document_url", sa.String(2048), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("institutional_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("number", sa.String(50), nullable=True),
        sa.Column("title", sa.String(500)),
        sa.Column("supplier_name", sa.String(500)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("total_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("monthly_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("institutional_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("title", sa.String(500)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("file_path", sa.String(1024), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("file_url", sa.String(2048), nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_from", sa.Date, nullable=True),
        sa.Column("valid_until", sa.Date, nullable=True),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("governance_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255)),
        sa.Column("role", sa.String(100)),
        sa.Column("body", sa.String(100)),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("governance_members")
    op.drop_table("institutional_documents")
    op.drop_table("institutional_contracts")
    op.drop_table("institutional_expenses")
    op.drop_table("institutional_revenues")
    op.drop_table("donation_receipts")
    op.drop_index("ix_webhook_provider_event")
    op.drop_table("payment_webhook_events")
    op.drop_table("donation_subscriptions")
    op.drop_table("donation_payments")
    op.drop_table("donations")
    op.drop_table("donation_campaigns")
    op.drop_table("donors")
