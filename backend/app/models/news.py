"""Modelos de notícias, classificações e revisão."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class NewsSource(BaseModel, TimestampMixin):
    """Fonte de notícias cadastrada."""

    __tablename__ = "news_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="journalistic")
    country: Mapped[str] = mapped_column(String(2), default="BR")
    language: Mapped[str] = mapped_column(String(5), default="pt")
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    credibility_status: Mapped[str] = mapped_column(String(50), default="unknown")
    terms_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class NewsArticle(BaseModel, TimestampMixin):
    """Artigo de notícia coletado."""

    __tablename__ = "news_articles"

    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("news_sources.id"), nullable=True, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(500), nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    original_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="pt")
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="collected", index=True)


class NewsMention(BaseModel, TimestampMixin):
    """Menção de um político em uma notícia."""

    __tablename__ = "news_mentions"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("news_articles.id"), index=True
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    mention_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_primary_subject: Mapped[bool] = mapped_column(Boolean, default=False)
    identity_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    resolution_status: Mapped[str] = mapped_column(String(50), default="pending")


class NewsClassification(BaseModel, TimestampMixin):
    """Classificação de impacto de uma notícia sobre um político."""

    __tablename__ = "news_classifications"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("news_articles.id"), index=True
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    # Classification
    sentiment: Mapped[str] = mapped_column(String(20))
    reputational_impact: Mapped[str] = mapped_column(String(20))
    impact_intensity: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String(50), index=True)
    fact_type: Mapped[str] = mapped_column(String(50), default="unclear")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    # Content
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Review
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True)
    review_reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # AI metadata
    model_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class NewsCluster(BaseModel, TimestampMixin):
    """Agrupamento de notícias sobre o mesmo acontecimento."""

    __tablename__ = "news_clusters"

    cluster_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    event_title: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    first_published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    article_count: Mapped[int] = mapped_column(Integer, default=1)
    representative_article_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )


class NewsContestation(BaseModel, TimestampMixin):
    """Contestação pública de uma classificação."""

    __tablename__ = "news_contestations"

    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("news_articles.id"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class AiUsageRecord(BaseModel):
    """Registro de uso da IA para controle de custos."""

    __tablename__ = "ai_usage_records"

    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    operation: Mapped[str] = mapped_column(String(50))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    article_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    politician_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
