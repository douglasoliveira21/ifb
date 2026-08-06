"""Politicians and related tables

Revision ID: 002
Revises: 001
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Political parties
    op.create_table(
        "political_parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("acronym", sa.String(20), unique=True, index=True),
        sa.Column("electoral_number", sa.Integer, nullable=True),
        sa.Column("logo_url", sa.String(2048), nullable=True),
        sa.Column("founded_at", sa.Date, nullable=True),
        sa.Column("dissolved_at", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("official_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Political positions
    op.create_table(
        "political_positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("government_level", sa.String(50), index=True),
        sa.Column("branch", sa.String(50), index=True),
        sa.Column("scope", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Politicians
    op.create_table(
        "politicians",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("full_name", sa.String(500), nullable=False, index=True),
        sa.Column("ballot_name", sa.String(255), nullable=True, index=True),
        sa.Column("slug", sa.String(300), unique=True, index=True),
        sa.Column("biography", sa.Text, nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
        sa.Column("birth_place", sa.String(255), nullable=True),
        sa.Column("nationality", sa.String(100), server_default="Brasileira"),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("marital_status", sa.String(50), nullable=True),
        sa.Column("education", sa.String(255), nullable=True),
        sa.Column("occupation", sa.String(255), nullable=True),
        sa.Column("photo_url", sa.String(2048), nullable=True),
        sa.Column("current_status", sa.String(100), server_default="unknown", index=True),
        sa.Column("current_party_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_parties.id"), nullable=True),
        sa.Column("current_position_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_positions.id"), nullable=True),
        sa.Column("state_code", sa.String(2), nullable=True, index=True),
        sa.Column("city_name", sa.String(255), nullable=True),
        sa.Column("website_url", sa.String(2048), nullable=True),
        sa.Column("is_public", sa.Boolean, server_default="false", index=True),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("data_quality_score", sa.Float, nullable=True),
        sa.Column("cpf_hash", sa.String(128), nullable=True, unique=True),
        # Audit mixin
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("updated_by", sa.String(255), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_by", sa.String(255), nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Politician aliases
    op.create_table(
        "politician_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True, nullable=False),
        sa.Column("alias", sa.String(500), nullable=False),
        sa.Column("normalized_alias", sa.String(500), nullable=False, index=True),
        sa.Column("alias_type", sa.String(50), server_default="ballot_name"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Social links
    op.create_table(
        "politician_social_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True, nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("is_official", sa.Boolean, server_default="false"),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Party memberships
    op.create_table(
        "party_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True, nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_parties.id"), index=True, nullable=False),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("state_code", sa.String(2), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("is_current", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Political mandates
    op.create_table(
        "political_mandates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True, nullable=False),
        sa.Column("position_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_positions.id"), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_parties.id"), nullable=True),
        sa.Column("state_code", sa.String(2), nullable=True),
        sa.Column("city_name", sa.String(255), nullable=True),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), server_default="in_office"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Change history
    op.create_table(
        "politician_change_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), index=True, nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),
        sa.Column("change_reason", sa.String(255), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("changed_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("politician_change_history")
    op.drop_table("political_mandates")
    op.drop_table("party_memberships")
    op.drop_table("politician_social_links")
    op.drop_table("politician_aliases")
    op.drop_table("politicians")
    op.drop_table("political_positions")
    op.drop_table("political_parties")
