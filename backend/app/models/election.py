"""Modelos de eleições, candidaturas, bens, receitas, despesas e resultados."""

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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class Election(BaseModel, TimestampMixin):
    """Eleição."""

    __tablename__ = "elections"

    tse_election_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    election_type: Mapped[str] = mapped_column(String(50), index=True)
    scope: Mapped[str] = mapped_column(String(50))
    rounds: Mapped[int] = mapped_column(Integer, default=1)
    first_round_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    second_round_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="concluded")
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class Candidacy(BaseModel, TimestampMixin):
    """Candidatura vinculada a uma eleição."""

    __tablename__ = "candidacies"

    politician_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), nullable=True, index=True
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("elections.id"), index=True
    )
    tse_candidate_id: Mapped[str | None] = mapped_column(String(50), index=True)
    sequence_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ballot_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ballot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)
    cpf_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_parties.id"), nullable=True
    )
    position_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_positions.id"), nullable=True
    )
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    city_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(100), default="deferido", index=True)
    status_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reelection: Mapped[bool] = mapped_column(Boolean, default=False)
    occupation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    race_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    coalition_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coalition_parties: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    # Reconciliation
    reconciliation_status: Mapped[str] = mapped_column(String(50), default="pending")
    reconciliation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    politician: Mapped["Politician | None"] = relationship(
        "Politician", foreign_keys=[politician_id]
    )
    election: Mapped["Election"] = relationship()
    party: Mapped["PoliticalParty | None"] = relationship(
        "PoliticalParty", foreign_keys=[party_id]
    )
    position: Mapped["PoliticalPosition | None"] = relationship(
        "PoliticalPosition", foreign_keys=[position_id]
    )


class CandidateAsset(BaseModel, TimestampMixin):
    """Bem declarado à Justiça Eleitoral."""

    __tablename__ = "candidate_assets"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    declared_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CampaignRevenue(BaseModel, TimestampMixin):
    """Receita de campanha eleitoral."""

    __tablename__ = "campaign_revenues"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    receipt_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    donor_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    donor_document_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    donor_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    revenue_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    received_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CampaignExpense(BaseModel, TimestampMixin):
    """Despesa de campanha eleitoral."""

    __tablename__ = "campaign_expenses"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    supplier_document_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    expense_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    contracted_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ElectionResult(BaseModel, TimestampMixin):
    """Resultado eleitoral de uma candidatura."""

    __tablename__ = "election_results"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    round: Mapped[int] = mapped_column(Integer, default=1)
    votes: Mapped[int] = mapped_column(Integer, default=0)
    vote_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_status: Mapped[str] = mapped_column(String(100), nullable=False)
    result_status_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
    elected: Mapped[bool] = mapped_column(Boolean, default=False)
    elected_by_average: Mapped[bool] = mapped_column(Boolean, default=False)
    substitute: Mapped[bool] = mapped_column(Boolean, default=False)
    ranking: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GovernmentPlan(BaseModel, TimestampMixin):
    """Plano de governo / proposta de candidatura."""

    __tablename__ = "government_plans"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class CampaignAccountability(BaseModel, TimestampMixin):
    """Prestação de contas de campanha."""

    __tablename__ = "campaign_accountability"

    candidacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidacies.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    judgment_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    judged_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ExternalDataset(BaseModel, TimestampMixin):
    """Dataset externo registrado para importação."""

    __tablename__ = "external_datasets"

    source_name: Mapped[str] = mapped_column(String(100), index=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    dataset_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    resource_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_modified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="discovered")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
