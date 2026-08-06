"""Modelos de indicadores, metodologias, resultados e rankings."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TimestampMixin


class IndicatorDefinition(BaseModel, TimestampMixin):
    """Definição de um indicador do IFB."""

    __tablename__ = "indicator_definitions"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    scope: Mapped[str] = mapped_column(String(50), default="politician")
    value_type: Mapped[str] = mapped_column(String(50), default="percentage")
    minimum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    maximum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, default=True)
    public: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class IndicatorMethodology(BaseModel, TimestampMixin):
    """Versão de metodologia de cálculo de um indicador."""

    __tablename__ = "indicator_methodologies"

    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicator_definitions.id"), index=True
    )
    version: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    formula_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    minimum_data_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    effective_until: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IndicatorResult(BaseModel, TimestampMixin):
    """Resultado calculado de um indicador para um político."""

    __tablename__ = "indicator_results"

    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicator_definitions.id"), index=True
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    methodology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicator_methodologies.id")
    )
    # Result
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="calculated", index=True)
    period_start: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    # Explanation
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitations_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Inputs snapshot (for reproducibility)
    inputs_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sources_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Metadata
    calculation_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class IndicatorContestation(BaseModel, TimestampMixin):
    """Contestação de resultado de indicador."""

    __tablename__ = "indicator_contestations"

    result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicator_results.id"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class RankingView(BaseModel, TimestampMixin):
    """Ranking público pré-calculado por dimensão."""

    __tablename__ = "ranking_views"

    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicator_definitions.id")
    )
    scope_position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scope_house: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scope_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    min_data_quality: Mapped[float] = mapped_column(Float, default=0.7)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    entries_count: Mapped[int] = mapped_column(Integer, default=0)
    public: Mapped[bool] = mapped_column(Boolean, default=True)
