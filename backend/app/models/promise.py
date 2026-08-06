"""Modelos de promessas de campanha, evidências e avaliações."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class CampaignPromise(BaseModel, TimestampMixin):
    """Promessa de campanha extraída de plano de governo."""

    __tablename__ = "campaign_promises"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    candidacy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), nullable=True, index=True
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("government_plans.id"), nullable=True
    )
    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="electoral_plan")
    # Classification
    category: Mapped[str] = mapped_column(String(50), index=True)
    promise_type: Mapped[str] = mapped_column(String(50), default="qualitative")
    government_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    responsible_branch: Mapped[str | None] = mapped_column(String(50), nullable=True)
    competence_status: Mapped[str] = mapped_column(String(50), default="unclear")
    # Target
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    deadline_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deadline_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    geographic_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Status
    status: Mapped[str] = mapped_column(String(50), default="not_started", index=True)
    progress_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Editorial
    editorial_status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    requires_double_review: Mapped[bool] = mapped_column(Boolean, default=False)
    # AI metadata
    extracted_by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Review
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    second_reviewer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    second_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    methodology_version: Mapped[str | None] = mapped_column(String(50), nullable=True)


class PromiseEvidence(BaseModel, TimestampMixin):
    """Evidência vinculada a uma promessa."""

    __tablename__ = "promise_evidences"

    promise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign_promises.id"), index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    supports_progress: Mapped[bool] = mapped_column(Boolean, default=True)
    contradicts_progress: Mapped[bool] = mapped_column(Boolean, default=False)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)


class PromiseAssessment(BaseModel, TimestampMixin):
    """Avaliação periódica de uma promessa."""

    __tablename__ = "promise_assessments"

    promise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign_promises.id"), index=True
    )
    assessment_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50))
    progress_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    evidence_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    assessed_by: Mapped[str] = mapped_column(String(255))
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PromiseStatusHistory(BaseModel):
    """Histórico de mudanças de status."""

    __tablename__ = "promise_status_history"

    promise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign_promises.id"), index=True
    )
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )


class PromiseContestation(BaseModel, TimestampMixin):
    """Contestação pública de promessa."""

    __tablename__ = "promise_contestations"

    promise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign_promises.id"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class PromiseExtractionJob(BaseModel, TimestampMixin):
    """Job de extração de promessas de um documento."""

    __tablename__ = "promise_extraction_jobs"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("government_plans.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    processed_pages: Mapped[int] = mapped_column(Integer, default=0)
    candidates_found: Mapped[int] = mapped_column(Integer, default=0)
    rejected: Mapped[int] = mapped_column(Integer, default=0)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
