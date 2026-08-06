"""Serviço de auditoria para registrar eventos de segurança."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditService:
    """Registra eventos de auditoria no banco de dados."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        *,
        user_id: uuid.UUID | None = None,
        user_email: str | None = None,
        resource_id: str | None = None,
        details: dict | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        correlation_id: str | None = None,
        justification: str | None = None,
    ) -> AuditLog:
        """Cria registro de auditoria."""
        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            justification=justification,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry


# --- Event constants ---

class AuditEvents:
    """Constantes para eventos de auditoria."""

    # Auth
    USER_REGISTERED = "user.registered"
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILED = "auth.login.failed"
    LOGIN_BLOCKED = "auth.login.blocked"
    LOGOUT = "auth.logout"
    TOKEN_REFRESHED = "auth.token.refreshed"
    TOKEN_REPLAY_DETECTED = "auth.token.replay"
    PASSWORD_CHANGED = "auth.password.changed"
    PASSWORD_RESET_REQUESTED = "auth.password.reset_requested"
    PASSWORD_RESET_COMPLETED = "auth.password.reset_completed"
    EMAIL_VERIFIED = "auth.email.verified"
    EMAIL_VERIFICATION_SENT = "auth.email.verification_sent"
    ACCOUNT_LOCKED = "auth.account.locked"
    ACCOUNT_UNLOCKED = "auth.account.unlocked"

    # Sessions
    SESSION_CREATED = "session.created"
    SESSION_REVOKED = "session.revoked"
    ALL_SESSIONS_REVOKED = "session.all_revoked"

    # MFA
    MFA_ENABLED = "auth.mfa.enabled"
    MFA_DISABLED = "auth.mfa.disabled"
    MFA_RECOVERY_USED = "auth.mfa.recovery_used"
    MFA_CODES_REGENERATED = "auth.mfa.codes_regenerated"

    # Profile
    PROFILE_UPDATED = "user.profile.updated"
    ACCOUNT_DELETED = "user.account.deleted"

    # RBAC
    ROLE_ASSIGNED = "rbac.role.assigned"
    ROLE_REMOVED = "rbac.role.removed"
    ROLE_CREATED = "rbac.role.created"
    ROLE_UPDATED = "rbac.role.updated"
    ROLE_DELETED = "rbac.role.deleted"
