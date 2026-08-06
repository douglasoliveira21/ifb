"""Legislative integration tables (Câmara and Senado)

Revision ID: 004
Revises: 003
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "legislative_houses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), unique=True),
        sa.Column("acronym", sa.String(20), unique=True),
        sa.Column("api_base_url", sa.String(2048), nullable=True),
        sa.Column("level", sa.String(50), server_default="federal"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "legislators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("external_id", sa.String(50), index=True),
        sa.Column("full_name", sa.String(500)),
        sa.Column("civil_name", sa.String(500), nullable=True),
        sa.Column("photo_url", sa.String(2048), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
        sa.Column("state_code", sa.String(2), nullable=True),
        sa.Column("party_acronym", sa.String(20), nullable=True),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_legislators_house_ext", "legislators", ["house_id", "external_id"], unique=True)

    op.create_table(
        "politician_legislative_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id")),
        sa.Column("match_method", sa.String(50)),
        sa.Column("match_confidence", sa.Float, server_default="0"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "legislative_propositions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("external_id", sa.String(50), index=True),
        sa.Column("type_acronym", sa.String(20)),
        sa.Column("number", sa.Integer, nullable=True),
        sa.Column("year", sa.Integer, nullable=True, index=True),
        sa.Column("title", sa.String(1000), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("full_text_url", sa.String(2048), nullable=True),
        sa.Column("status", sa.String(100), nullable=True, index=True),
        sa.Column("presentation_date", sa.Date, nullable=True),
        sa.Column("last_event_date", sa.Date, nullable=True),
        sa.Column("topics", sa.Text, nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "proposition_authors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("proposition_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_propositions.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), nullable=True),
        sa.Column("author_name", sa.String(500)),
        sa.Column("author_type", sa.String(50), server_default="legislator"),
        sa.Column("is_primary", sa.Boolean, server_default="false"),
    )

    op.create_table(
        "legislative_vote_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("external_id", sa.String(50), index=True),
        sa.Column("proposition_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_propositions.id"), nullable=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("result", sa.String(100), nullable=True),
        sa.Column("is_nominal", sa.Boolean, server_default="true"),
        sa.Column("yes_votes", sa.Integer, nullable=True),
        sa.Column("no_votes", sa.Integer, nullable=True),
        sa.Column("abstentions", sa.Integer, nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "legislator_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("vote_event_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_vote_events.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("original_vote", sa.String(50)),
        sa.Column("normalized_vote", sa.String(50), index=True),
        sa.Column("party_at_vote", sa.String(20), nullable=True),
        sa.Column("state_at_vote", sa.String(2), nullable=True),
    )

    op.create_table(
        "session_attendance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("session_external_id", sa.String(100), nullable=True),
        sa.Column("session_date", sa.Date, nullable=True, index=True),
        sa.Column("session_type", sa.String(50), nullable=True),
        sa.Column("attendance_status", sa.String(50)),
        sa.Column("justification", sa.String(500), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "parliamentary_expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("year", sa.Integer, index=True),
        sa.Column("month", sa.Integer),
        sa.Column("category", sa.String(255)),
        sa.Column("supplier_name", sa.String(500), nullable=True),
        sa.Column("supplier_document_hash", sa.String(128), nullable=True),
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("document_date", sa.Date, nullable=True),
        sa.Column("gross_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("reimbursement_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("document_url", sa.String(2048), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "legislative_committees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("external_id", sa.String(50), index=True),
        sa.Column("name", sa.String(500)),
        sa.Column("acronym", sa.String(50), nullable=True),
        sa.Column("committee_type", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "committee_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("committee_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_committees.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("role", sa.String(100), server_default="member"),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "legislative_speeches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("house_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislative_houses.id"), index=True),
        sa.Column("legislator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legislators.id"), index=True),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("date", sa.Date, nullable=True, index=True),
        sa.Column("session_type", sa.String(100), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("full_text_url", sa.String(2048), nullable=True),
        sa.Column("topics", sa.Text, nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "sync_checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("provider", sa.String(50), index=True),
        sa.Column("resource", sa.String(100), index=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_external_update", sa.String(255), nullable=True),
        sa.Column("last_page", sa.Integer, nullable=True),
        sa.Column("last_external_id", sa.String(255), nullable=True),
        sa.Column("cursor", sa.String(1024), nullable=True),
        sa.Column("metadata_json", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sync_checkpoints_provider_resource", "sync_checkpoints",
                    ["provider", "resource"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_sync_checkpoints_provider_resource")
    op.drop_table("sync_checkpoints")
    op.drop_table("legislative_speeches")
    op.drop_table("committee_memberships")
    op.drop_table("legislative_committees")
    op.drop_table("parliamentary_expenses")
    op.drop_table("session_attendance")
    op.drop_table("legislator_votes")
    op.drop_table("legislative_vote_events")
    op.drop_table("proposition_authors")
    op.drop_table("legislative_propositions")
    op.drop_table("politician_legislative_profiles")
    op.drop_index("ix_legislators_house_ext")
    op.drop_table("legislators")
    op.drop_table("legislative_houses")
