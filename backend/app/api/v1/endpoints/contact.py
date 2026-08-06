"""Endpoint de contato público."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import build_rate_key, rate_limiter

router = APIRouter(tags=["Contato"])
logger = logging.getLogger(__name__)

VALID_SUBJECTS = {
    "Dúvida",
    "Correção de dados",
    "Contestação",
    "Imprensa",
    "Parceria",
    "Doação",
    "Outro",
}


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@router.post("/contact", status_code=201)
async def send_contact_message(
    data: ContactRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Recebe mensagem de contato (rate limited, auditado)."""
    ip = request.client.host if request.client else "unknown"

    # Rate limit: 5 mensagens por hora por IP
    key = build_rate_key("contact", ip)
    if await rate_limiter.is_rate_limited(key, max_attempts=5, window_seconds=3600):
        from app.core.exceptions import ValidationError
        raise ValidationError(detail="Limite de mensagens excedido. Tente novamente mais tarde.")
    await rate_limiter.increment(key, 3600)

    # Validate subject
    if data.subject not in VALID_SUBJECTS:
        from app.core.exceptions import ValidationError
        raise ValidationError(detail="Assunto inválido.")

    # Log the contact (in production, store in DB or send email)
    logger.info(
        "Contact message received: name=%s email=%s subject=%s ip=%s",
        data.name,
        data.email,
        data.subject,
        ip,
    )

    # TODO: Store in contact_messages table and/or dispatch email via Celery
    # For now, persist basic audit
    from app.services.audit import AuditService

    audit = AuditService(db)
    await audit.log(
        "CONTACT_MESSAGE_RECEIVED",
        "contact",
        details={
            "name": data.name,
            "email": data.email,
            "subject": data.subject,
            "message_length": len(data.message),
        },
        ip_address=ip,
    )

    return {"message": "Mensagem recebida com sucesso."}
