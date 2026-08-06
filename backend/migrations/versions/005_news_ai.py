"""News and AI classification tables

Revision ID: 005
Revises: 004
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "news_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), unique=True, index=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("source_type", sa.String(50), server_default="journalistic"),
        sa.Column("country", sa.String(2), server_default="BR"),
        sa.Column("language", sa.String(5), server_default="pt"),
        sa.Column("is_official", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("credibility_status", sa.String(50), server_default="unknown"),
        sa.Column("terms_url", sa.String(2048), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "news_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("cluster_key", sa.String(255), unique=True, index=True),
        sa.Column("event_title", sa.String(1000), nullable=True),
        sa.Column("first_published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("article_count", sa.Integer, server_default="1"),
        sa.Column("representative_article_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "news_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("news_sources.id"), nullable=True, index=True),
        sa.Column("provider", sa.String(50), index=True),
        sa.Column("external_id", sa.String(255), nullable=True, index=True),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content_excerpt", sa.Text, nullable=True),
        sa.Column("author", sa.String(500), nullable=True),
        sa.Column("canonical_url", sa.String(2048), nullable=False),
        sa.Column("original_url", sa.String(2048), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("language", sa.String(5), server_default="pt"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("content_hash", sa.String(64), nullable=True, index=True),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("status", sa.String(50), server_default="collected", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "news_mentions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("news_articles.id"), index=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), index=True),
        sa.Column("mention_text", sa.Text, nullable=True),
        sa.Column("is_primary_subject", sa.Boolean, server_default="false"),
        sa.Column("identity_confidence", sa.Float, server_default="0"),
        sa.Column("relevance_score", sa.Float, server_default="0"),
        sa.Column("resolution_status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "news_classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("news_articles.id"), index=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("politicians.id"), index=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("reputational_impact", sa.String(20)),
        sa.Column("impact_intensity", sa.Integer, server_default="0"),
        sa.Column("category", sa.String(50), index=True),
        sa.Column("fact_type", sa.String(50), server_default="unclear"),
        sa.Column("confidence", sa.Float, server_default="0"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("justification", sa.Text, nullable=True),
        sa.Column("evidence_json", postgresql.JSON, nullable=True),
        sa.Column("requires_human_review", sa.Boolean, server_default="true"),
        sa.Column("review_reasons", postgresql.JSON, nullable=True),
        sa.Column("review_status", sa.String(50), server_default="pending", index=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_provider", sa.String(50), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "news_contestations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("news_articles.id"), index=True),
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
        "ai_usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("provider", sa.String(50)),
        sa.Column("model", sa.String(100)),
        sa.Column("operation", sa.String(50)),
        sa.Column("input_tokens", sa.Integer, server_default="0"),
        sa.Column("output_tokens", sa.Integer, server_default="0"),
        sa.Column("estimated_cost", sa.Float, server_default="0"),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ai_usage_records")
    op.drop_table("news_contestations")
    op.drop_table("news_classifications")
    op.drop_table("news_mentions")
    op.drop_table("news_articles")
    op.drop_table("news_clusters")
    op.drop_table("news_sources")
