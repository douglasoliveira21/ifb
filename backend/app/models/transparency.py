"""Modelos de transparência institucional do IFB."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TimestampMixin


class InstitutionalRevenue(BaseModel, TimestampMixin):
    """Receita institucional do IFB."""

    __tablename__ = "institutional_revenues"

    date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(500))
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    fee_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    source_type: Mapped[str] = mapped_column(String(50))
    donation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    public: Mapped[bool] = mapped_column(Boolean, default=True)


class InstitutionalExpense(BaseModel, TimestampMixin):
    """Despesa institucional do IFB."""

    __tablename__ = "institutional_expenses"

    date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    competence_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    supplier_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(500))
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    public: Mapped[bool] = mapped_column(Boolean, default=True)


class InstitutionalContract(BaseModel, TimestampMixin):
    """Contrato institucional do IFB."""

    __tablename__ = "institutional_contracts"

    number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    supplier_name: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    total_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    monthly_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    public: Mapped[bool] = mapped_column(Boolean, default=True)


class InstitutionalDocument(BaseModel, TimestampMixin):
    """Documento institucional público."""

    __tablename__ = "institutional_documents"

    category: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    public: Mapped[bool] = mapped_column(Boolean, default=True)


class GovernanceMember(BaseModel, TimestampMixin):
    """Membro de governança do IFB."""

    __tablename__ = "governance_members"

    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    public: Mapped[bool] = mapped_column(Boolean, default=True)
