"""Schemas de autenticação e autorização."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Register ---


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)


class RegisterResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    message: str = "Conta criada. Verifique seu e-mail para ativar."


# --- Login ---


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    mfa_required: bool = False


# --- Refresh ---


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


# --- Email Verification ---


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# --- Password Reset ---


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=10, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10, max_length=128)


# --- Sessions ---


class SessionInfo(BaseModel):
    id: uuid.UUID
    user_agent: str | None
    ip_address: str | None
    created_at: datetime
    last_used_at: datetime | None
    is_current: bool = False


class SessionListResponse(BaseModel):
    sessions: list[SessionInfo]


# --- MFA ---


class MfaSetupResponse(BaseModel):
    secret: str
    qr_code_uri: str
    recovery_codes: list[str]
    challenge_id: str = ""


class MfaConfirmRequest(BaseModel):
    code: str


class MfaVerifyRequest(BaseModel):
    code: str


class MfaRecoveryRequest(BaseModel):
    recovery_code: str


# --- User Profile ---


class UserMeResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_verified: bool
    mfa_enabled: bool
    avatar_url: str | None
    created_at: datetime
    roles: list[str]


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    avatar_url: str | None = None


# --- Generic ---


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
