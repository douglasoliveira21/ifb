"""Modelos SQLAlchemy do IFB."""

from app.models.base import AuditMixin, BaseModel, TimestampMixin
from app.models.user import (
    EmailVerificationToken, MfaRecoveryCode, PasswordResetToken,
    Permission, Role, RolePermission, Session, User, UserRole,
)
from app.models.audit import AuditLog
from app.models.politician import (
    Politician, PoliticianAlias, PoliticianChangeHistory,
    PoliticianSocialLink, PoliticalMandate, PoliticalParty,
    PoliticalPosition, PartyMembership,
)
from app.models.election import (
    Election, Candidacy, CandidateAsset, CampaignRevenue,
    CampaignExpense, ElectionResult, GovernmentPlan,
    CampaignAccountability, ExternalDataset,
)
from app.models.legislative import (
    LegislativeHouse, Legislator, PoliticianLegislativeProfile,
    LegislativeProposition, PropositionAuthor, LegislativeVoteEvent,
    LegislatorVote, SessionAttendance, ParliamentaryExpense,
    LegislativeCommittee, CommitteeMembership, LegislativeSpeech,
    SyncCheckpoint,
)

__all__ = [
    "BaseModel", "TimestampMixin", "AuditMixin",
    "User", "Role", "Permission", "UserRole", "RolePermission", "Session",
    "EmailVerificationToken", "PasswordResetToken", "MfaRecoveryCode", "AuditLog",
    "Politician", "PoliticianAlias", "PoliticianChangeHistory",
    "PoliticianSocialLink", "PoliticalMandate", "PoliticalParty",
    "PoliticalPosition", "PartyMembership",
    "Election", "Candidacy", "CandidateAsset", "CampaignRevenue",
    "CampaignExpense", "ElectionResult", "GovernmentPlan",
    "CampaignAccountability", "ExternalDataset",
    "LegislativeHouse", "Legislator", "PoliticianLegislativeProfile",
    "LegislativeProposition", "PropositionAuthor", "LegislativeVoteEvent",
    "LegislatorVote", "SessionAttendance", "ParliamentaryExpense",
    "LegislativeCommittee", "CommitteeMembership", "LegislativeSpeech",
    "SyncCheckpoint",
]
