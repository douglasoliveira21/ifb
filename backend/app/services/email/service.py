"""Serviço de envio de e-mail assíncrono."""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> bool:
    """
    Envia e-mail via SMTP assíncrono.
    Retorna True se enviado com sucesso, False em caso de erro.
    """
    if not settings.smtp_host:
        logger.warning("SMTP não configurado. E-mail não enviado para %s", to)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            use_tls=settings.smtp_port == 465,
            start_tls=settings.smtp_port == 587,
        )
        logger.info("E-mail enviado para %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("Falha ao enviar e-mail para %s: %s", to, str(e))
        return False


async def send_verification_email(to: str, token: str) -> bool:
    """Envia e-mail de verificação de conta."""
    verification_url = f"{settings.frontend_url}/verificar-email?token={token}"
    subject = "Verifique seu e-mail — Instituto Fiscaliza Brasil"
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0A0A0A;">Verifique seu e-mail</h2>
        <p>Você criou uma conta no Instituto Fiscaliza Brasil.</p>
        <p>Clique no botão abaixo para verificar seu e-mail:</p>
        <a href="{verification_url}"
           style="display: inline-block; background: #FFC400; color: #0A0A0A;
                  padding: 12px 24px; text-decoration: none; border-radius: 6px;
                  font-weight: bold;">
            Verificar e-mail
        </a>
        <p style="margin-top: 20px; color: #666; font-size: 14px;">
            Este link expira em 24 horas. Se você não criou esta conta, ignore este e-mail.
        </p>
    </div>
    """
    return await send_email(to, subject, html)


async def send_password_reset_email(to: str, token: str) -> bool:
    """Envia e-mail de recuperação de senha."""
    reset_url = f"{settings.frontend_url}/redefinir-senha?token={token}"
    subject = "Redefinição de senha — Instituto Fiscaliza Brasil"
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0A0A0A;">Redefinição de senha</h2>
        <p>Você solicitou a redefinição de sua senha.</p>
        <p>Clique no botão abaixo para criar uma nova senha:</p>
        <a href="{reset_url}"
           style="display: inline-block; background: #FFC400; color: #0A0A0A;
                  padding: 12px 24px; text-decoration: none; border-radius: 6px;
                  font-weight: bold;">
            Redefinir senha
        </a>
        <p style="margin-top: 20px; color: #666; font-size: 14px;">
            Este link expira em 1 hora. Se você não fez esta solicitação, ignore este e-mail.
        </p>
    </div>
    """
    return await send_email(to, subject, html)


async def send_password_changed_email(to: str) -> bool:
    """Notifica que a senha foi alterada."""
    subject = "Senha alterada — Instituto Fiscaliza Brasil"
    html = """
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0A0A0A;">Senha alterada</h2>
        <p>Sua senha foi alterada com sucesso.</p>
        <p style="color: #D93025;">Se você não fez esta alteração, entre em contato imediatamente.</p>
    </div>
    """
    return await send_email(to, subject, html)


async def send_mfa_changed_email(to: str, enabled: bool) -> bool:
    """Notifica alteração de MFA."""
    action = "ativada" if enabled else "desativada"
    subject = f"Autenticação em dois fatores {action} — IFB"
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0A0A0A;">MFA {action}</h2>
        <p>A autenticação em dois fatores foi {action} na sua conta.</p>
        <p style="color: #D93025;">Se você não fez esta alteração, entre em contato imediatamente.</p>
    </div>
    """
    return await send_email(to, subject, html)
