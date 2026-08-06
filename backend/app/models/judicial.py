"""Modelos de processos judiciais, partes, movimentações e decisões."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TimestampMixin


class JudicialCase(BaseModel, TimestampMixin):
    """Processo judicial público."""

    __tablename__ = "judicial_cases"

    court_system: Mapped[str] = mapped_column(String(50), index=True)
    tribunal: Mapped[str] = mapped_column(String(100), index=True)
    court_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    case_number: Mapped[str] = mapped_column(String(50), index=True)
    case_number_hash: Mapped[str] = mapped_column(String(64), index=True)
    case_class_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    case_class_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instance: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    judging_body: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin_unit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    filing_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    last_movement_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    secrecy_level: Mapped[int] = mapped_column(Integer, default=0)
    public_access: Mapped[bool] = mapped_column(Boolean, default=True)
    # Status
    original_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_status: Mapped[str] = mapped_column(String(50), default="unknown", index=True)
    procedural_status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    # Category
    case_category: Mapped[str] = mapped_column(String(50), default="unknown", index=True)
    # Source
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Editorial
    editorial_status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    review_status: Mapped[str] = mapped_column(String(50), default="pending")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JudicialCaseParty(BaseModel, TimestampMixin):
    """Parte envolvida em um processo."""

    __tablename__ = "judicial_case_parties"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    politician_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), nullable=True, index=True
    )
    party_name: Mapped[str] = mapped_column(String(500))
    party_name_normalized: Mapped[str | None] = mapped_column(String(500), nullable=True)
    party_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role_original: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role_normalized: Mapped[str] = mapped_column(String(50), default="unknown")
    identity_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    match_status: Mapped[str] = mapped_column(String(50), default="pending")
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class JudicialMovement(BaseModel, TimestampMixin):
    """Movimentação processual."""

    __tablename__ = "judicial_movements"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    movement_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    movement_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    movement_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    movement_date: Mapped[datetime | None] = mapped_column(Date, nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JudicialDecision(BaseModel, TimestampMixin):
    """Decisão judicial."""

    __tablename__ = "judicial_decisions"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    decision_type: Mapped[str] = mapped_column(String(100))
    decision_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    judge_or_body: Mapped[str | None] = mapped_column(String(500), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    original_text_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_outcome: Mapped[str] = mapped_column(String(50), default="pending")
    appealable: Mapped[bool] = mapped_column(Boolean, default=True)
    final: Mapped[bool] = mapped_column(Boolean, default=False)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    review_status: Mapped[str] = mapped_column(String(50), default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)


class JudicialAppeal(BaseModel, TimestampMixin):
    """Recurso em processo judicial."""

    __tablename__ = "judicial_appeals"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    appeal_type: Mapped[str] = mapped_column(String(100))
    filed_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    appellant: Mapped[str | None] = mapped_column(String(500), nullable=True)
    destination_court: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class JudicialCaseMatch(BaseModel, TimestampMixin):
    """Correspondência entre processo e político (conciliação)."""

    __tablename__ = "judicial_case_matches"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_case_parties.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    match_method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JudicialContestation(BaseModel, TimestampMixin):
    """Contestação pública de informação judicial."""

    __tablename__ = "judicial_contestations"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("judicial_cases.id"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
