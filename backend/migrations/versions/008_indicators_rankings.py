"""Indicators and rankings tables

Revision ID: 008
Revises: 007
Create Date: 2026-08-05
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "indicator_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(50), unique=True, index=True),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("scope", sa.String(50), server_default="politician"),
        sa.Column("value_type", sa.String(50), server_default="percentage"),
        sa.Column("minimum_value", sa.Float, nullable=True),
        sa.Column("maximum_value", sa.Float, nullable=True),
        sa.Column("higher_is_better", sa.Boolean, server_default="true"),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "indicator_methodologies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("indicator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("indicator_definitions.id"), index=True),
        sa.Column("version", sa.String(20)),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("formula", sa.Text, nullable=True),
        sa.Column("formula_json", postgresql.JSON, nullable=True),
        sa.Column("minimum_data_requirements", sa.Text, nullable=True),
        sa.Column("limitations", sa.Text, nullable=True),
        sa.Column("effective_from", sa.Date, nullable=True),
        sa.Column("effective_until", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), server_default="draft", index=True),
        sa.Column("approved_by", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "indicator_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("indicator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("indicator_definitions.id"), index=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), index=True),
        sa.Column("methodology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("indicator_methodologies.id"), nullable=True),
        sa.Column("value", sa.Float, nullable=True),
        sa.Column("status", sa.String(50), server_default="calculated", index=True),
        sa.Column("period_start", sa.Date, nullable=True),
        sa.Column("period_end", sa.Date, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("limitations_json", postgresql.JSON, nullable=True),
        sa.Column("inputs_json", postgresql.JSON, nullable=True),
        sa.Column("sources_json", postgresql.JSON, nullable=True),
        sa.Column("calculation_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "indicator_contestations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("result_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("indicator_results.id"), index=True),
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

    op.create_table(
        "ranking_views",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(50), index=True),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("indicator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("indicator_definitions.id")),
        sa.Column("scope_position", sa.String(100), nullable=True),
        sa.Column("scope_house", sa.String(50), nullable=True),
        sa.Column("scope_state", sa.String(2), nullable=True),
        sa.Column("period_start", sa.Date, nullable=True),
        sa.Column("period_end", sa.Date, nullable=True),
        sa.Column("min_data_quality", sa.Float, server_default="0.7"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entries_count", sa.Integer, server_default="0"),
        sa.Column("public", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("ranking_views")
    op.drop_table("indicator_contestations")
    op.drop_table("indicator_results")
    op.drop_table("indicator_methodologies")
    op.drop_table("indicator_definitions")
