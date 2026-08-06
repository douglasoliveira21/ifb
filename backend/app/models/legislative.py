"""Modelos legislativos — Câmara dos Deputados e Senado Federal."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class LegislativeHouse(BaseModel, TimestampMixin):
    """Casa legislativa (Câmara ou Senado)."""

    __tablename__ = "legislative_houses"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    acronym: Mapped[str] = mapped_column(String(20), unique=True)
    api_base_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    level: Mapped[str] = mapped_column(String(50), default="federal")


class Legislator(BaseModel, TimestampMixin):
    """Parlamentar externo (dados da fonte oficial)."""

    __tablename__ = "legislators"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(50), index=True)
    full_name: Mapped[str] = mapped_column(String(500))
    civil_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    party_acronym: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PoliticianLegislativeProfile(BaseModel, TimestampMixin):
    """Vínculo entre político IFB e parlamentar externo."""

    __tablename__ = "politician_legislative_profiles"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id")
    )
    match_method: Mapped[str] = mapped_column(String(50))
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LegislativeProposition(BaseModel, TimestampMixin):
    """Proposição legislativa (PL, PEC, etc.)."""

    __tablename__ = "legislative_propositions"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(50), index=True)
    type_acronym: Mapped[str] = mapped_column(String(20))
    number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    presentation_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    last_event_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PropositionAuthor(BaseModel):
    """Autor de proposição."""

    __tablename__ = "proposition_authors"

    proposition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_propositions.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), nullable=True
    )
    author_name: Mapped[str] = mapped_column(String(500))
    author_type: Mapped[str] = mapped_column(String(50), default="legislator")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)


class LegislativeVoteEvent(BaseModel, TimestampMixin):
    """Evento de votação."""

    __tablename__ = "legislative_vote_events"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(50), index=True)
    proposition_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_propositions.id"), nullable=True
    )
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_nominal: Mapped[bool] = mapped_column(Boolean, default=True)
    yes_votes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    no_votes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    abstentions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class LegislatorVote(BaseModel):
    """Voto individual de um parlamentar."""

    __tablename__ = "legislator_votes"

    vote_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_vote_events.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    original_vote: Mapped[str] = mapped_column(String(50))
    normalized_vote: Mapped[str] = mapped_column(String(50), index=True)
    party_at_vote: Mapped[str | None] = mapped_column(String(20), nullable=True)
    state_at_vote: Mapped[str | None] = mapped_column(String(2), nullable=True)


class SessionAttendance(BaseModel, TimestampMixin):
    """Presença em sessão legislativa."""

    __tablename__ = "session_attendance"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    session_external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_date: Mapped[datetime | None] = mapped_column(Date, nullable=True, index=True)
    session_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    attendance_status: Mapped[str] = mapped_column(String(50))
    justification: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class ParliamentaryExpense(BaseModel, TimestampMixin):
    """Despesa parlamentar (cota, CEAP, etc.)."""

    __tablename__ = "parliamentary_expenses"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(255))
    supplier_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    supplier_document_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    reimbursement_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    document_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class LegislativeCommittee(BaseModel, TimestampMixin):
    """Comissão legislativa."""

    __tablename__ = "legislative_committees"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(500))
    acronym: Mapped[str | None] = mapped_column(String(50), nullable=True)
    committee_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class CommitteeMembership(BaseModel, TimestampMixin):
    """Participação em comissão."""

    __tablename__ = "committee_memberships"

    committee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_committees.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(100), default="member")
    started_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)


class LegislativeSpeech(BaseModel, TimestampMixin):
    """Discurso parlamentar."""

    __tablename__ = "legislative_speeches"

    house_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislative_houses.id"), index=True
    )
    legislator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("legislators.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date: Mapped[datetime | None] = mapped_column(Date, nullable=True, index=True)
    session_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class SyncCheckpoint(BaseModel, TimestampMixin):
    """Checkpoint de sincronização incremental."""

    __tablename__ = "sync_checkpoints"

    provider: Mapped[str] = mapped_column(String(50), index=True)
    resource: Mapped[str] = mapped_column(String(100), index=True)
    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_external_update: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cursor: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
