"""Modelos de políticos, partidos, filiações e mandatos."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, BaseModel, TimestampMixin


class PoliticalParty(BaseModel, TimestampMixin):
    """Partido político."""

    __tablename__ = "political_parties"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    acronym: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    electoral_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    founded_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    dissolved_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    official_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class PoliticalPosition(BaseModel, TimestampMixin):
    """Cargo político (Deputado Federal, Senador, Prefeito, etc.)."""

    __tablename__ = "political_positions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    government_level: Mapped[str] = mapped_column(String(50), index=True)
    branch: Mapped[str] = mapped_column(String(50), index=True)
    scope: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Politician(BaseModel, TimestampMixin, AuditMixin):
    """Político ou agente público — entidade central."""

    __tablename__ = "politicians"

    full_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    ballot_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    slug: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    birth_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), default="Brasileira")
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Current status
    current_status: Mapped[str] = mapped_column(String(100), default="unknown", index=True)
    current_party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_parties.id"), nullable=True
    )
    current_position_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_positions.id"), nullable=True
    )
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    city_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Administrative
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    data_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Sensitive identifiers (encrypted/hashed)
    cpf_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)

    # Relationships
    current_party: Mapped["PoliticalParty | None"] = relationship(foreign_keys=[current_party_id])
    current_position: Mapped["PoliticalPosition | None"] = relationship(
        foreign_keys=[current_position_id]
    )
    aliases: Mapped[list["PoliticianAlias"]] = relationship(back_populates="politician", lazy="selectin")
    social_links: Mapped[list["PoliticianSocialLink"]] = relationship(
        back_populates="politician", lazy="noload"
    )
    memberships: Mapped[list["PartyMembership"]] = relationship(
        back_populates="politician", lazy="noload"
    )
    mandates: Mapped[list["PoliticalMandate"]] = relationship(
        back_populates="politician", lazy="noload"
    )


class PoliticianAlias(BaseModel, TimestampMixin):
    """Nome alternativo / alias de um político."""

    __tablename__ = "politician_aliases"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    alias: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    alias_type: Mapped[str] = mapped_column(String(50), default="ballot_name")
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    politician: Mapped["Politician"] = relationship(back_populates="aliases")


class PoliticianSocialLink(BaseModel, TimestampMixin):
    """Redes sociais e links oficiais."""

    __tablename__ = "politician_social_links"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    politician: Mapped["Politician"] = relationship(back_populates="social_links")


class PartyMembership(BaseModel, TimestampMixin):
    """Histórico de filiações partidárias."""

    __tablename__ = "party_memberships"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_parties.id"), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    politician: Mapped["Politician"] = relationship(back_populates="memberships")
    party: Mapped["PoliticalParty"] = relationship()


class PoliticalMandate(BaseModel, TimestampMixin):
    """Mandato político exercido."""

    __tablename__ = "political_mandates"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    position_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_positions.id")
    )
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("political_parties.id"), nullable=True
    )
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="in_office")
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    politician: Mapped["Politician"] = relationship(back_populates="mandates")
    position: Mapped["PoliticalPosition"] = relationship()
    party: Mapped["PoliticalParty | None"] = relationship()


class PoliticianChangeHistory(BaseModel):
    """Histórico de alterações em políticos."""

    __tablename__ = "politician_change_history"

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("politicians.id"), index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
