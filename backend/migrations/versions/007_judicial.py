"""Judicial cases tables

Revision ID: 007
Revises: 006
Create Date: 2026-08-05
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "judicial_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("court_system", sa.String(50), index=True),
        sa.Column("tribunal", sa.String(100), index=True),
        sa.Column("court_code", sa.String(20), nullable=True),
        sa.Column("case_number", sa.String(50), index=True),
        sa.Column("case_number_hash", sa.String(64), index=True),
        sa.Column("case_class_code", sa.String(20), nullable=True),
        sa.Column("case_class_name", sa.String(255), nullable=True),
        sa.Column("jurisdiction", sa.String(100), nullable=True),
        sa.Column("instance", sa.String(50), nullable=True, index=True),
        sa.Column("judging_body", sa.String(255), nullable=True),
        sa.Column("origin_unit", sa.String(255), nullable=True),
        sa.Column("filing_date", sa.Date, nullable=True),
        sa.Column("last_movement_date", sa.Date, nullable=True),
        sa.Column("secrecy_level", sa.Integer, server_default="0"),
        sa.Column("public_access", sa.Boolean, server_default="true"),
        sa.Column("original_status", sa.String(255), nullable=True),
        sa.Column("normalized_status", sa.String(50), server_default="unknown", index=True),
        sa.Column("procedural_status", sa.String(50), server_default="active", index=True),
        sa.Column("case_category", sa.String(50), server_default="unknown", index=True),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("editorial_status", sa.String(50), server_default="draft", index=True),
        sa.Column("review_status", sa.String(50), server_default="pending"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_case_parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), nullable=True, index=True),
        sa.Column("party_name", sa.String(500)),
        sa.Column("party_name_normalized", sa.String(500), nullable=True),
        sa.Column("party_type", sa.String(50), nullable=True),
        sa.Column("role_original", sa.String(100), nullable=True),
        sa.Column("role_normalized", sa.String(50), server_default="unknown"),
        sa.Column("identity_confidence", sa.Float, server_default="0"),
        sa.Column("match_status", sa.String(50), server_default="pending"),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("movement_code", sa.String(20), nullable=True),
        sa.Column("movement_name", sa.String(255), nullable=True),
        sa.Column("movement_text", sa.Text, nullable=True),
        sa.Column("movement_date", sa.Date, nullable=True, index=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("decision_type", sa.String(100)),
        sa.Column("decision_date", sa.Date, nullable=True),
        sa.Column("judge_or_body", sa.String(500), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("full_text_url", sa.String(2048), nullable=True),
        sa.Column("original_text_excerpt", sa.Text, nullable=True),
        sa.Column("normalized_outcome", sa.String(50), server_default="pending"),
        sa.Column("appealable", sa.Boolean, server_default="true"),
        sa.Column("final", sa.Boolean, server_default="false"),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("review_status", sa.String(50), server_default="pending"),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_appeals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("appeal_type", sa.String(100)),
        sa.Column("filed_at", sa.Date, nullable=True),
        sa.Column("appellant", sa.String(500), nullable=True),
        sa.Column("destination_court", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("decision", sa.Text, nullable=True),
        sa.Column("decided_at", sa.Date, nullable=True),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_case_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), index=True),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_case_parties.id"), nullable=True),
        sa.Column("confidence", sa.Float, server_default="0"),
        sa.Column("match_method", sa.String(50)),
        sa.Column("status", sa.String(50), server_default="pending", index=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "judicial_contestations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("judicial_cases.id"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.String(100)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), server_default="pending", index=True),
        sa.Column("resolved_by", sa.String(255), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("judicial_contestations")
    op.drop_table("judicial_case_matches")
    op.drop_table("judicial_appeals")
    op.drop_table("judicial_decisions")
    op.drop_table("judicial_movements")
    op.drop_table("judicial_case_parties")
    op.drop_table("judicial_cases")
