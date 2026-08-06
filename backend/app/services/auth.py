"""Serviço de autenticação e gerenciamento de sessões."""

import uuid
from datetime import UTC, datetime, timedelta

import pyotp
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
    verify_token_hash,
)
from app.models.user import (
    EmailVerificationToken,
    MfaRecoveryCode,
    PasswordResetToken,
    Role,
    Session,
    User,
    UserRole,
)
from app.services.audit import AuditEvents, AuditService

settings = get_settings()


ACCOUNT_LOCK_THRESHOLD = 5
ACCOUNT_LOCK_DURATION_MINUTES = 15
EMAIL_TOKEN_EXPIRY_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = 1
MFA_RECOVERY_CODES_COUNT = 10


class AuthService:
    """Gerencia autenticação, sessões e tokens."""

    def __init__(self, db: AsyncSession, audit: AuditService) -> None:
        self.db = db
        self.audit = audit

    # --- Registration ---

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str]:
        """
        Registra novo usuário. Retorna (user, verification_token).
        """
        # Validate password
        errors = validate_password_strength(password)
        if errors:
            raise ValidationError(detail=errors[0])

        # Check duplicate
        existing = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        if existing.scalar_one_or_none():
            raise ConflictError(detail="E-mail já cadastrado.")

        # Create user
        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            is_active=True,
            is_verified=False,
            password_changed_at=datetime.now(UTC),
        )
        self.db.add(user)
        await self.db.flush()

        # Assign default role (user)
        default_role = await self.db.execute(
            select(Role).where(Role.name == "user")
        )
        role = default_role.scalar_one_or_none()
        if role:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            self.db.add(user_role)

        # Generate verification token
        token = generate_secure_token()
        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=EMAIL_TOKEN_EXPIRY_HOURS),
        )
        self.db.add(verification)
        await self.db.flush()

        # Audit
        await self.audit.log(
            AuditEvents.USER_REGISTERED,
            "user",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return user, token

    # --- Login ---

    async def login(
        self,
        email: str,
        password: str,
        mfa_code: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, str, bool]:
        """
        Autentica usuário.
        Retorna (access_token, refresh_token, session_id, mfa_required).
        Se mfa_required=True, access_token será parcial (precisa de MFA).
        """
        # Find user (generic error to prevent enumeration)
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if not user:
            # Timing-safe: still hash to prevent timing attacks
            hash_password("dummy_password_for_timing")
            await self.audit.log(
                AuditEvents.LOGIN_FAILED,
                "auth",
                details={"reason": "user_not_found"},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise UnauthorizedError(detail="Credenciais inválidas.")

        # Check account lock
        if user.locked_until and user.locked_until > datetime.now(UTC):
            await self.audit.log(
                AuditEvents.LOGIN_BLOCKED,
                "auth",
                user_id=user.id,
                user_email=user.email,
                ip_address=ip_address,
            )
            raise UnauthorizedError(detail="Credenciais inválidas.")

        # Verify password
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= ACCOUNT_LOCK_THRESHOLD:
                user.locked_until = datetime.now(UTC) + timedelta(
                    minutes=ACCOUNT_LOCK_DURATION_MINUTES
                )
                await self.audit.log(
                    AuditEvents.ACCOUNT_LOCKED,
                    "auth",
                    user_id=user.id,
                    user_email=user.email,
                    ip_address=ip_address,
                )
            await self.audit.log(
                AuditEvents.LOGIN_FAILED,
                "auth",
                user_id=user.id,
                user_email=user.email,
                details={"attempts": user.failed_login_attempts},
                ip_address=ip_address,
            )
            await self.db.flush()
            raise UnauthorizedError(detail="Credenciais inválidas.")

        # Check if MFA required
        if user.mfa_enabled:
            if not mfa_code:
                # Return partial auth - MFA still needed
                partial_token = create_access_token(
                    subject=str(user.id),
                    extra_claims={"mfa_verified": False},
                )
                return partial_token, "", "", True

            # Verify MFA code
            if not self._verify_totp(user.mfa_secret, mfa_code):
                # Try recovery code
                if not await self._use_recovery_code(user.id, mfa_code):
                    await self.audit.log(
                        AuditEvents.LOGIN_FAILED,
                        "auth",
                        user_id=user.id,
                        details={"reason": "invalid_mfa"},
                        ip_address=ip_address,
                    )
                    raise UnauthorizedError(detail="Credenciais inválidas.")

        # Success - reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)
        await self.db.flush()

        # Create session and tokens
        access_token, refresh_token, session_id = await self._create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await self.audit.log(
            AuditEvents.LOGIN_SUCCESS,
            "auth",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return access_token, refresh_token, session_id, False

    # --- Session Management ---

    async def _create_session(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, str]:
        """Creates session with tokens. Returns (access, refresh, session_id)."""
        roles = [ur.role.name for ur in user.roles]
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"roles": roles, "mfa_verified": True},
        )

        refresh_raw, token_family = create_refresh_token(subject=str(user.id))

        session = Session(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_raw),
            token_family=token_family,
            user_agent=user_agent,
            ip_address=ip_address,
            is_active=True,
            expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expires_days),
            last_used_at=datetime.now(UTC),
        )
        self.db.add(session)
        await self.db.flush()

        return access_token, refresh_raw, str(session.id)

    async def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """
        Rotaciona refresh token.
        Retorna (new_access_token, new_refresh_token).
        Detecta replay e revoga família inteira.
        """
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError(detail="Token inválido.")

        user_id = payload.get("sub")
        token_family = payload.get("family")
        if not user_id or not token_family:
            raise UnauthorizedError(detail="Token inválido.")

        # Find active session for this family
        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.token_family == token_family,
                    Session.is_active == True,
                )
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            # Possible replay attack - revoke all sessions for this family
            await self._revoke_family(token_family, "replay_detected")
            await self.audit.log(
                AuditEvents.TOKEN_REPLAY_DETECTED,
                "auth",
                details={"family": token_family, "user_id": user_id},
                ip_address=ip_address,
            )
            raise UnauthorizedError(detail="Token inválido.")

        # Verify the token hash matches
        if not verify_token_hash(refresh_token, session.refresh_token_hash):
            # Token reuse detected - revoke entire family
            session.is_active = False
            session.revoked_at = datetime.now(UTC)
            session.revoke_reason = "replay_detected"
            await self.audit.log(
                AuditEvents.TOKEN_REPLAY_DETECTED,
                "auth",
                user_id=session.user_id,
                details={"session_id": str(session.id)},
                ip_address=ip_address,
            )
            await self.db.flush()
            raise UnauthorizedError(detail="Token inválido.")

        # Check expiration
        if session.expires_at < datetime.now(UTC):
            session.is_active = False
            session.revoke_reason = "expired"
            await self.db.flush()
            raise UnauthorizedError(detail="Sessão expirada.")

        # Get user
        user_result = await self.db.execute(
            select(User).where(User.id == session.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedError(detail="Token inválido.")

        # Rotate: generate new refresh token, update session
        roles = [ur.role.name for ur in user.roles]
        new_access = create_access_token(
            subject=str(user.id),
            extra_claims={"roles": roles, "mfa_verified": True},
        )
        new_refresh_raw, _ = create_refresh_token(
            subject=str(user.id), family=token_family
        )

        # Update session with new token hash
        session.refresh_token_hash = hash_token(new_refresh_raw)
        session.last_used_at = datetime.now(UTC)
        session.ip_address = ip_address
        await self.db.flush()

        return new_access, new_refresh_raw

    async def _revoke_family(self, token_family: str, reason: str) -> None:
        """Revoga todas as sessões de uma família de tokens."""
        result = await self.db.execute(
            select(Session).where(Session.token_family == token_family)
        )
        sessions = result.scalars().all()
        for s in sessions:
            s.is_active = False
            s.revoked_at = datetime.now(UTC)
            s.revoke_reason = reason
        await self.db.flush()

    async def logout(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> None:
        """Encerra sessão específica (logout)."""
        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.id == session_id,
                    Session.user_id == user_id,
                    Session.is_active == True,
                )
            )
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_active = False
            session.revoked_at = datetime.now(UTC)
            session.revoke_reason = "logout"
            await self.db.flush()

        await self.audit.log(
            AuditEvents.LOGOUT,
            "auth",
            user_id=user_id,
            ip_address=ip_address,
        )

    async def revoke_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID, ip: str | None = None
    ) -> None:
        """Revoga uma sessão específica do usuário."""
        result = await self.db.execute(
            select(Session).where(
                and_(Session.id == session_id, Session.user_id == user_id)
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            return
        session.is_active = False
        session.revoked_at = datetime.now(UTC)
        session.revoke_reason = "user_revoked"
        await self.db.flush()
        await self.audit.log(
            AuditEvents.SESSION_REVOKED, "session",
            user_id=user_id, resource_id=str(session_id), ip_address=ip,
        )

    async def revoke_all_sessions(
        self, user_id: uuid.UUID, ip: str | None = None
    ) -> int:
        """Revoga todas as sessões de um usuário. Retorna quantidade."""
        result = await self.db.execute(
            select(Session).where(
                and_(Session.user_id == user_id, Session.is_active == True)
            )
        )
        sessions = result.scalars().all()
        count = 0
        for s in sessions:
            s.is_active = False
            s.revoked_at = datetime.now(UTC)
            s.revoke_reason = "all_revoked"
            count += 1
        await self.db.flush()
        await self.audit.log(
            AuditEvents.ALL_SESSIONS_REVOKED, "session",
            user_id=user_id, details={"count": count}, ip_address=ip,
        )
        return count

    async def get_user_sessions(self, user_id: uuid.UUID) -> list[Session]:
        """Retorna sessões ativas do usuário."""
        result = await self.db.execute(
            select(Session).where(
                and_(Session.user_id == user_id, Session.is_active == True)
            ).order_by(Session.last_used_at.desc())
        )
        return list(result.scalars().all())

    # --- Email Verification ---

    async def verify_email(self, token: str, ip: str | None = None) -> bool:
        """Verifica e-mail usando token. Retorna True se sucesso."""
        token_h = hash_token(token)
        result = await self.db.execute(
            select(EmailVerificationToken).where(
                and_(
                    EmailVerificationToken.token_hash == token_h,
                    EmailVerificationToken.used_at == None,
                )
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            return False
        if record.expires_at < datetime.now(UTC):
            return False

        # Mark token as used
        record.used_at = datetime.now(UTC)

        # Verify user
        user_result = await self.db.execute(
            select(User).where(User.id == record.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False
        user.is_verified = True
        await self.db.flush()

        await self.audit.log(
            AuditEvents.EMAIL_VERIFIED, "auth",
            user_id=user.id, user_email=user.email, ip_address=ip,
        )
        return True

    async def resend_verification(
        self, email: str, ip: str | None = None
    ) -> str | None:
        """
        Gera novo token de verificação. Retorna token ou None se não encontrado.
        Externamente, sempre retorna mensagem genérica.
        """
        result = await self.db.execute(
            select(User).where(
                and_(User.email == email.lower(), User.is_verified == False)
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        token = generate_secure_token()
        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=EMAIL_TOKEN_EXPIRY_HOURS),
        )
        self.db.add(verification)
        await self.db.flush()
        return token

    # --- Password Reset ---

    async def request_password_reset(
        self, email: str, ip: str | None = None
    ) -> str | None:
        """
        Gera token de reset. Retorna token ou None se não encontrado.
        Externamente, sempre retorna mensagem genérica.
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        token = generate_secure_token()
        reset_record = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(
                hours=PASSWORD_RESET_TOKEN_EXPIRY_HOURS
            ),
        )
        self.db.add(reset_record)
        await self.db.flush()

        await self.audit.log(
            AuditEvents.PASSWORD_RESET_REQUESTED, "auth",
            user_id=user.id, ip_address=ip,
        )
        return token

    async def reset_password(
        self, token: str, new_password: str, ip: str | None = None
    ) -> bool:
        """Redefine senha via token. Revoga todas as sessões."""
        errors = validate_password_strength(new_password)
        if errors:
            raise ValidationError(detail=errors[0])

        token_h = hash_token(token)
        result = await self.db.execute(
            select(PasswordResetToken).where(
                and_(
                    PasswordResetToken.token_hash == token_h,
                    PasswordResetToken.used_at == None,
                )
            )
        )
        record = result.scalar_one_or_none()
        if not record or record.expires_at < datetime.now(UTC):
            return False

        record.used_at = datetime.now(UTC)

        user_result = await self.db.execute(
            select(User).where(User.id == record.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False

        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.now(UTC)
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.db.flush()

        # Revoke all sessions
        await self.revoke_all_sessions(user.id, ip)

        await self.audit.log(
            AuditEvents.PASSWORD_RESET_COMPLETED, "auth",
            user_id=user.id, user_email=user.email, ip_address=ip,
        )
        return True

    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
        ip: str | None = None,
    ) -> None:
        """Altera senha do usuário autenticado."""
        errors = validate_password_strength(new_password)
        if errors:
            raise ValidationError(detail=errors[0])

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError()

        if not verify_password(current_password, user.password_hash):
            raise ForbiddenError(detail="Senha atual incorreta.")

        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.now(UTC)
        user.must_change_password = False
        await self.db.flush()

        await self.audit.log(
            AuditEvents.PASSWORD_CHANGED, "auth",
            user_id=user.id, user_email=user.email, ip_address=ip,
        )

    # --- MFA ---

    def _verify_totp(self, secret: str | None, code: str) -> bool:
        """Verifica código TOTP."""
        if not secret:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    async def setup_mfa(self, user_id: uuid.UUID) -> tuple[str, str, list[str]]:
        """
        Configura MFA para o usuário.
        Retorna (secret, otpauth_uri, recovery_codes).
        O secret deve ser confirmado antes de ativar.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError()
        if user.mfa_enabled:
            raise ConflictError(detail="MFA já está ativado.")

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Instituto Fiscaliza Brasil",
        )

        # Store secret temporarily (not yet confirmed)
        user.mfa_secret = secret
        await self.db.flush()

        # Generate recovery codes
        codes = [generate_secure_token(8)[:12] for _ in range(MFA_RECOVERY_CODES_COUNT)]
        return secret, uri, codes

    async def confirm_mfa(
        self,
        user_id: uuid.UUID,
        code: str,
        recovery_codes: list[str],
        ip: str | None = None,
    ) -> bool:
        """Confirma ativação do MFA com código TOTP válido."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.mfa_secret:
            return False

        if not self._verify_totp(user.mfa_secret, code):
            return False

        user.mfa_enabled = True
        await self.db.flush()

        # Store recovery codes as hashes
        for rc in recovery_codes:
            code_record = MfaRecoveryCode(
                user_id=user.id,
                code_hash=hash_token(rc),
            )
            self.db.add(code_record)
        await self.db.flush()

        await self.audit.log(
            AuditEvents.MFA_ENABLED, "auth",
            user_id=user.id, user_email=user.email, ip_address=ip,
        )
        return True

    async def disable_mfa(
        self,
        user_id: uuid.UUID,
        password: str,
        code: str,
        ip: str | None = None,
    ) -> None:
        """Desativa MFA. Requer senha + código TOTP."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError()
        if not user.mfa_enabled:
            raise ValidationError(detail="MFA não está ativado.")

        if not verify_password(password, user.password_hash):
            raise ForbiddenError(detail="Senha incorreta.")
        if not self._verify_totp(user.mfa_secret, code):
            raise ForbiddenError(detail="Código MFA inválido.")

        user.mfa_enabled = False
        user.mfa_secret = None
        await self.db.flush()

        # Remove recovery codes
        codes_result = await self.db.execute(
            select(MfaRecoveryCode).where(MfaRecoveryCode.user_id == user.id)
        )
        for c in codes_result.scalars().all():
            await self.db.delete(c)
        await self.db.flush()

        await self.audit.log(
            AuditEvents.MFA_DISABLED, "auth",
            user_id=user.id, user_email=user.email, ip_address=ip,
        )

    async def _use_recovery_code(self, user_id: uuid.UUID, code: str) -> bool:
        """Tenta usar código de recuperação MFA. Retorna True se válido."""
        code_hash = hash_token(code)
        result = await self.db.execute(
            select(MfaRecoveryCode).where(
                and_(
                    MfaRecoveryCode.user_id == user_id,
                    MfaRecoveryCode.code_hash == code_hash,
                    MfaRecoveryCode.used_at == None,
                )
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            return False

        record.used_at = datetime.now(UTC)
        await self.db.flush()

        await self.audit.log(
            AuditEvents.MFA_RECOVERY_USED, "auth",
            user_id=user_id,
        )
        return True

    async def regenerate_recovery_codes(
        self,
        user_id: uuid.UUID,
        password: str,
        code: str,
        ip: str | None = None,
    ) -> list[str]:
        """Regenera códigos de recuperação MFA."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.mfa_enabled:
            raise ValidationError(detail="MFA não está ativado.")

        if not verify_password(password, user.password_hash):
            raise ForbiddenError(detail="Senha incorreta.")
        if not self._verify_totp(user.mfa_secret, code):
            raise ForbiddenError(detail="Código MFA inválido.")

        # Remove old codes
        old_codes = await self.db.execute(
            select(MfaRecoveryCode).where(MfaRecoveryCode.user_id == user.id)
        )
        for c in old_codes.scalars().all():
            await self.db.delete(c)

        # Generate new codes
        codes = [generate_secure_token(8)[:12] for _ in range(MFA_RECOVERY_CODES_COUNT)]
        for rc in codes:
            self.db.add(MfaRecoveryCode(
                user_id=user.id, code_hash=hash_token(rc)
            ))
        await self.db.flush()

        await self.audit.log(
            AuditEvents.MFA_CODES_REGENERATED, "auth",
            user_id=user.id, ip_address=ip,
        )
        return codes

    # --- User Management ---

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retorna usuário por ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        user_id: uuid.UUID,
        full_name: str | None = None,
        avatar_url: str | None = None,
        ip: str | None = None,
    ) -> User:
        """Atualiza perfil do usuário."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError()

        if full_name is not None:
            user.full_name = full_name.strip()
        if avatar_url is not None:
            user.avatar_url = avatar_url

        await self.db.flush()
        await self.audit.log(
            AuditEvents.PROFILE_UPDATED, "user",
            user_id=user.id, ip_address=ip,
        )
        return user

    async def delete_account(
        self, user_id: uuid.UUID, password: str, ip: str | None = None
    ) -> None:
        """Soft delete da conta do usuário."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError()
        if not verify_password(password, user.password_hash):
            raise ForbiddenError(detail="Senha incorreta.")

        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        await self.revoke_all_sessions(user.id, ip)
        await self.db.flush()

        await self.audit.log(
            AuditEvents.ACCOUNT_DELETED, "user",
            user_id=user.id, ip_address=ip,
        )
