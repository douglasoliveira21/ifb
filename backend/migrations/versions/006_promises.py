"""Campaign promises tables

Revision ID: 006
Revises: 005
Create Date: 2026-08-05
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "campaign_promises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), index=True),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidacies.id"), nullable=True, index=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("government_plans.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_excerpt", sa.Text, nullable=True),
        sa.Column("source_page", sa.Integer, nullable=True),
        sa.Column("source_type", sa.String(50), server_default="electoral_plan"),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("promise_type", sa.String(50), server_default="qualitative"),
        sa.Column("government_level", sa.String(50), nullable=True),
        sa.Column("responsible_branch", sa.String(50), nullable=True),
        sa.Column("competence_status", sa.String(50), server_default="unclear"),
        sa.Column("target_value", sa.Float, nullable=True),
        sa.Column("target_unit", sa.String(100), nullable=True),
        sa.Column("baseline_value", sa.Float, nullable=True),
        sa.Column("deadline_text", sa.String(255), nullable=True),
        sa.Column("deadline_date", sa.Date, nullable=True),
        sa.Column("geographic_scope", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), server_default="not_started", index=True),
        sa.Column("progress_percentage", sa.Float, nullable=True),
        sa.Column("current_value", sa.Float, nullable=True),
        sa.Column("editorial_status", sa.String(50), server_default="draft", index=True),
        sa.Column("extraction_confidence", sa.Float, server_default="0"),
        sa.Column("requires_double_review", sa.Boolean, server_default="false"),
        sa.Column("extracted_by_ai", sa.Boolean, server_default="false"),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("ai_prompt_version", sa.String(50), nullable=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("second_reviewer", sa.String(255), nullable=True),
        sa.Column("second_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("methodology_version", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "promise_evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("promise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaign_promises.id"), index=True),
        sa.Column("evidence_type", sa.String(50)),
        sa.Column("title", sa.String(500)),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("source_name", sa.String(255), nullable=True),
        sa.Column("document_date", sa.Date, nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("supports_progress", sa.Boolean, server_default="true"),
        sa.Column("contradicts_progress", sa.Boolean, server_default="false"),
        sa.Column("value", sa.Float, nullable=True),
        sa.Column("unit", sa.String(100), nullable=True),
        sa.Column("verified", sa.Boolean, server_default="false"),
        sa.Column("verified_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "promise_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("promise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaign_promises.id"), index=True),
        sa.Column("assessment_date", sa.Date, nullable=False),
        sa.Column("status", sa.String(50)),
        sa.Column("progress_percentage", sa.Float, nullable=True),
        sa.Column("current_value", sa.Float, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("methodology_version", sa.String(50), nullable=True),
        sa.Column("evidence_snapshot", postgresql.JSON, nullable=True),
        sa.Column("assessed_by", sa.String(255)),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "promise_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("promise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaign_promises.id"), index=True),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50)),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("changed_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "promise_contestations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("promise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaign_promises.id"), index=True),
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
        "promise_extraction_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("government_plans.id"), index=True),
        sa.Column("status", sa.String(50), server_default="pending", index=True),
        sa.Column("total_pages", sa.Integer, server_default="0"),
        sa.Column("processed_pages", sa.Integer, server_default="0"),
        sa.Column("candidates_found", sa.Integer, server_default="0"),
        sa.Column("rejected", sa.Integer, server_default="0"),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("tokens_used", sa.Integer, server_default="0"),
        sa.Column("estimated_cost", sa.Float, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("requested_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("promise_extraction_jobs")
    op.drop_table("promise_contestations")
    op.drop_table("promise_status_history")
    op.drop_table("promise_assessments")
    op.drop_table("promise_evidences")
    op.drop_table("campaign_promises")
