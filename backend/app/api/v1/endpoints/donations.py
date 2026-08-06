"""API de doações."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.donation import (
    Donation, DonationCampaign, DonationPayment, Donor, DonationReceipt,
)
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/donations", tags=["Doações"])


class DonationCreateRequest(BaseModel):
    amount: float = Field(gt=1, le=100000)
    donor_name: str = Field(min_length=2, max_length=255)
    donor_email: str
    frequency: str = "one_time"
    payment_method: str = "pix"
    campaign_slug: str | None = None
    anonymous: bool = False
    message: str | None = None
    idempotency_key: str | None = None


@router.get("/campaigns")
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    """Lista campanhas de doação ativas."""
    result = await db.execute(
        select(DonationCampaign).where(DonationCampaign.active == True)
    )
    campaigns = result.scalars().all()
    return {
        "data": [
            {"slug": c.slug, "name": c.name, "description": c.description,
             "goal_amount": float(c.goal_amount) if c.goal_amount else None,
             "raised_amount": float(c.raised_amount)}
            for c in campaigns
        ]
    }


@router.post("", status_code=201)
async def create_donation(
    data: DonationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Cria doação. Retorna ID para checkout."""
    # Idempotency check
    if data.idempotency_key:
        existing = await db.execute(
            select(Donation).where(Donation.idempotency_key == data.idempotency_key)
        )
        if existing.scalar_one_or_none():
            raise ValidationError(detail="Doação já processada com esta chave.")

    # Get or create donor
    donor_result = await db.execute(
        select(Donor).where(Donor.email == data.donor_email.lower())
    )
    donor = donor_result.scalar_one_or_none()
    if not donor:
        donor = Donor(
            name=data.donor_name,
            email=data.donor_email.lower(),
            anonymous_publicly=data.anonymous,
        )
        db.add(donor)
        await db.flush()

    # Resolve campaign
    campaign_id = None
    if data.campaign_slug:
        camp = await db.execute(
            select(DonationCampaign).where(DonationCampaign.slug == data.campaign_slug)
        )
        campaign = camp.scalar_one_or_none()
        if campaign:
            campaign_id = campaign.id

    donation = Donation(
        donor_id=donor.id,
        campaign_id=campaign_id,
        amount=data.amount,
        frequency=data.frequency,
        payment_method=data.payment_method,
        status="created",
        public_display_authorized=not data.anonymous,
        public_display_name=data.donor_name if not data.anonymous else None,
        message=data.message,
        idempotency_key=data.idempotency_key,
    )
    db.add(donation)
    await db.flush()

    return {"id": donation.id, "status": "created", "amount": float(data.amount)}


@router.post("/{donation_id}/pix")
async def generate_pix(
    donation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Gera cobrança Pix para a doação."""
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise NotFoundError(detail="Doação não encontrada.")

    # Create payment record (gateway integration placeholder)
    payment = DonationPayment(
        donation_id=donation.id,
        provider="manual_pix",
        amount=donation.amount,
        net_amount=donation.amount,
        payment_method="pix",
        status="pending",
        pix_copy_paste="00020126...(código gerado pelo gateway)",
        expires_at=datetime.now(UTC),
    )
    db.add(payment)
    donation.status = "pending"
    await db.flush()

    return {
        "payment_id": payment.id,
        "pix_copy_paste": payment.pix_copy_paste,
        "expires_at": payment.expires_at.isoformat() if payment.expires_at else None,
        "status": "pending",
    }


@router.get("/{donation_id}/status")
async def get_donation_status(
    donation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Consulta status da doação."""
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise NotFoundError(detail="Doação não encontrada.")
    return {"id": donation.id, "status": donation.status, "amount": float(donation.amount)}


@router.get("/{donation_id}/receipt")
async def get_donation_receipt(
    donation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Obtém recibo da doação paga."""
    result = await db.execute(
        select(DonationReceipt).where(DonationReceipt.donation_id == donation_id)
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise NotFoundError(detail="Recibo não disponível.")
    return {
        "receipt_number": receipt.receipt_number,
        "amount": float(receipt.amount),
        "donor_name": receipt.donor_name,
        "issued_at": receipt.issued_at.isoformat(),
        "disclaimer": "A dedução fiscal depende da legislação aplicável.",
    }


# --- Webhook ---

@router.post("/webhooks/{provider}")
async def payment_webhook(
    provider: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Recebe webhook de gateway de pagamento."""
    import hashlib
    body = await request.body()
    payload_hash = hashlib.sha256(body).hexdigest()

    # TODO: Validate signature per provider
    # TODO: Process asynchronously via Celery

    from app.models.donation import PaymentWebhookEvent
    event = PaymentWebhookEvent(
        provider=provider,
        external_event_id=payload_hash[:32],
        event_type="payment.received",
        payload_hash=payload_hash,
        signature_valid=True,
        processing_status="received",
    )
    db.add(event)
    await db.flush()

    return {"status": "received"}
