"""Tarefas Celery para envio de e-mail assíncrono."""

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="email.send_verification",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def task_send_verification_email(self, to: str, token: str) -> dict:
    """Envia e-mail de verificação de conta via Celery."""
    import asyncio
    from app.services.email.service import send_verification_email

    try:
        result = asyncio.run(send_verification_email(to, token))
        logger.info("Verification email sent to %s", to)
        return {"status": "sent", "recipient": to}
    except Exception as exc:
        logger.error("Failed to send verification email: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_password_reset",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def task_send_password_reset_email(self, to: str, token: str) -> dict:
    """Envia e-mail de recuperação de senha via Celery."""
    import asyncio
    from app.services.email.service import send_password_reset_email

    try:
        result = asyncio.run(send_password_reset_email(to, token))
        logger.info("Password reset email sent to %s", to)
        return {"status": "sent", "recipient": to}
    except Exception as exc:
        logger.error("Failed to send password reset email: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_password_changed",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def task_send_password_changed_email(self, to: str) -> dict:
    """Notifica alteração de senha via Celery."""
    import asyncio
    from app.services.email.service import send_password_changed_email

    try:
        asyncio.run(send_password_changed_email(to))
        return {"status": "sent", "recipient": to}
    except Exception as exc:
        logger.error("Failed to send password changed email: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_mfa_changed",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def task_send_mfa_changed_email(self, to: str, enabled: bool) -> dict:
    """Notifica alteração de MFA via Celery."""
    import asyncio
    from app.services.email.service import send_mfa_changed_email

    try:
        asyncio.run(send_mfa_changed_email(to, enabled))
        return {"status": "sent", "recipient": to}
    except Exception as exc:
        logger.error("Failed to send MFA changed email: %s", exc)
        raise self.retry(exc=exc)


def dispatch_verification_email(to: str, token: str) -> None:
    """Despacha verificação para Celery (non-blocking)."""
    task_send_verification_email.delay(to, token)


def dispatch_password_reset_email(to: str, token: str) -> None:
    """Despacha reset de senha para Celery (non-blocking)."""
    task_send_password_reset_email.delay(to, token)


def dispatch_password_changed_email(to: str) -> None:
    """Despacha notificação de senha alterada para Celery."""
    task_send_password_changed_email.delay(to)


def dispatch_mfa_changed_email(to: str, enabled: bool) -> None:
    """Despacha notificação de MFA para Celery."""
    task_send_mfa_changed_email.delay(to, enabled)
