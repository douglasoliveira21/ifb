"""Modelos de doações, pagamentos e recibos."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TimestampMixin


class Donor(BaseModel, TimestampMixin):
    """Doador do IFB."""

    __tablename__ = "donors"

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), index=True)
    document_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    donor_type: Mapped[str] = mapped_column(String(20), default="individual")
    anonymous_publicly: Mapped[bool] = mapped_column(Boolean, default=False)
    communication_consent: Mapped[bool] = mapped_column(Boolean, default=False)


class DonationCampaign(BaseModel, TimestampMixin):
    """Campanha de doação."""

    __tablename__ = "donation_campaigns"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    raised_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Donation(BaseModel, TimestampMixin):
    """Doação individual."""

    __tablename__ = "donations"

    donor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donors.id"), index=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donation_campaigns.id"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    frequency: Mapped[str] = mapped_column(String(20), default="one_time")
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created", index=True)
    public_display_authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    public_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DonationPayment(BaseModel, TimestampMixin):
    """Pagamento de uma doação."""

    __tablename__ = "donation_payments"

    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donations.id"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    external_payment_id: Mapped[str | None] = mapped_column(String(255), index=True)
    external_checkout_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    fee_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    pix_qr_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    pix_copy_paste: Mapped[str | None] = mapped_column(Text, nullable=True)
    checkout_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DonationSubscription(BaseModel, TimestampMixin):
    """Assinatura recorrente de doação."""

    __tablename__ = "donation_subscriptions"

    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donations.id"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    external_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    frequency: Mapped[str] = mapped_column(String(20), default="monthly")
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    next_billing_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_payment_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PaymentWebhookEvent(BaseModel):
    """Evento recebido via webhook de gateway."""

    __tablename__ = "payment_webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    external_event_id: Mapped[str] = mapped_column(String(255), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload_hash: Mapped[str] = mapped_column(String(64))
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="received")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DonationReceipt(BaseModel, TimestampMixin):
    """Recibo de doação."""

    __tablename__ = "donation_receipts"

    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donations.id"), index=True
    )
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    donor_name: Mapped[str] = mapped_column(String(255))
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
