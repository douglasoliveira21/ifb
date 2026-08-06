"""Serviço de gestão de políticos."""

import re
import unicodedata
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.politician import (
    PartyMembership,
    Politician,
    PoliticianAlias,
    PoliticianChangeHistory,
    PoliticianSocialLink,
    PoliticalMandate,
    PoliticalParty,
    PoliticalPosition,
)
from app.services.audit import AuditEvents, AuditService


def normalize_text(text: str) -> str:
    """Remove acentos e normaliza para busca."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def generate_slug(name: str) -> str:
    """Gera slug a partir do nome."""
    slug = normalize_text(name)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


class PoliticianService:
    """Gerencia criação, edição, pesquisa e publicação de políticos."""

    def __init__(self, db: AsyncSession, audit: AuditService) -> None:
        self.db = db
        self.audit = audit

    async def create(
        self,
        full_name: str,
        created_by: str,
        *,
        ballot_name: str | None = None,
        biography: str | None = None,
        birth_date=None,
        birth_place: str | None = None,
        gender: str | None = None,
        marital_status: str | None = None,
        education: str | None = None,
        occupation: str | None = None,
        photo_url: str | None = None,
        state_code: str | None = None,
        city_name: str | None = None,
        website_url: str | None = None,
        current_party_id: uuid.UUID | None = None,
        current_position_id: uuid.UUID | None = None,
        source_url: str | None = None,
        ip: str | None = None,
    ) -> Politician:
        """Cria novo político."""
        slug = generate_slug(full_name)

        # Ensure unique slug
        existing = await self.db.execute(
            select(Politician).where(Politician.slug == slug)
        )
        if existing.scalar_one_or_none():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        politician = Politician(
            full_name=full_name.strip(),
            ballot_name=ballot_name,
            slug=slug,
            biography=biography,
            birth_date=birth_date,
            birth_place=birth_place,
            gender=gender,
            marital_status=marital_status,
            education=education,
            occupation=occupation,
            photo_url=photo_url,
            state_code=state_code.upper() if state_code else None,
            city_name=city_name,
            website_url=website_url,
            current_party_id=current_party_id,
            current_position_id=current_position_id,
            current_status="unknown",
            is_public=False,
            is_verified=False,
            created_by=created_by,
            source_url=source_url,
        )
        self.db.add(politician)
        await self.db.flush()

        # Create ballot_name alias if provided
        if ballot_name:
            alias = PoliticianAlias(
                politician_id=politician.id,
                alias=ballot_name,
                normalized_alias=normalize_text(ballot_name),
                alias_type="ballot_name",
            )
            self.db.add(alias)
            await self.db.flush()

        await self.audit.log(
            "politician.created", "politician",
            resource_id=str(politician.id),
            details={"name": full_name},
            ip_address=ip,
        )
        return politician


    async def update(
        self,
        politician_id: uuid.UUID,
        updated_by: str,
        *,
        ip: str | None = None,
        **fields,
    ) -> Politician:
        """Atualiza político e registra histórico de alterações."""
        result = await self.db.execute(
            select(Politician).where(Politician.id == politician_id)
        )
        politician = result.scalar_one_or_none()
        if not politician:
            raise NotFoundError(detail="Político não encontrado.")

        for field_name, new_value in fields.items():
            if new_value is None:
                continue
            old_value = getattr(politician, field_name, None)
            if old_value == new_value:
                continue

            setattr(politician, field_name, new_value)

            # Record change history
            history = PoliticianChangeHistory(
                politician_id=politician.id,
                field_name=field_name,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value),
                change_reason="admin_update",
                changed_by=updated_by,
            )
            self.db.add(history)

        politician.updated_by = updated_by
        politician.version = (politician.version or 1) + 1
        await self.db.flush()

        await self.audit.log(
            "politician.updated", "politician",
            resource_id=str(politician.id),
            details={"fields": list(fields.keys())},
            ip_address=ip,
        )
        return politician

    async def publish(self, politician_id: uuid.UUID, published_by: str, ip: str | None = None) -> None:
        """Publica político (torna visível na API pública)."""
        result = await self.db.execute(select(Politician).where(Politician.id == politician_id))
        politician = result.scalar_one_or_none()
        if not politician:
            raise NotFoundError(detail="Político não encontrado.")
        politician.is_public = True
        await self.db.flush()
        await self.audit.log(
            "politician.published", "politician",
            resource_id=str(politician.id), ip_address=ip,
        )

    async def unpublish(self, politician_id: uuid.UUID, ip: str | None = None) -> None:
        """Despublica político."""
        result = await self.db.execute(select(Politician).where(Politician.id == politician_id))
        politician = result.scalar_one_or_none()
        if not politician:
            raise NotFoundError(detail="Político não encontrado.")
        politician.is_public = False
        await self.db.flush()

    async def soft_delete(self, politician_id: uuid.UUID, ip: str | None = None) -> None:
        """Soft delete."""
        result = await self.db.execute(select(Politician).where(Politician.id == politician_id))
        politician = result.scalar_one_or_none()
        if not politician:
            raise NotFoundError(detail="Político não encontrado.")
        politician.deleted_at = datetime.now(UTC)
        politician.is_public = False
        await self.db.flush()

    async def get_by_id(self, politician_id: uuid.UUID) -> Politician | None:
        result = await self.db.execute(select(Politician).where(Politician.id == politician_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Politician | None:
        result = await self.db.execute(
            select(Politician).where(Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None)
        )
        return result.scalar_one_or_none()


    async def search(
        self,
        q: str | None = None,
        party: str | None = None,
        state: str | None = None,
        position: str | None = None,
        page: int = 1,
        limit: int = 20,
        include_unpublished: bool = False,
    ) -> tuple[list[Politician], int]:
        """
        Pesquisa políticos com filtros.
        Retorna (resultados, total).
        """
        query = select(Politician).where(Politician.deleted_at == None)

        if not include_unpublished:
            query = query.where(Politician.is_public == True)

        if q:
            normalized = normalize_text(q)
            search_term = f"%{normalized}%"
            # Search in name, ballot_name and aliases
            query = query.where(
                or_(
                    func.lower(Politician.full_name).contains(q.lower()),
                    func.lower(Politician.ballot_name).contains(q.lower()),
                    Politician.id.in_(
                        select(PoliticianAlias.politician_id).where(
                            PoliticianAlias.normalized_alias.contains(normalized)
                        )
                    ),
                )
            )

        if party:
            query = query.where(
                Politician.current_party_id.in_(
                    select(PoliticalParty.id).where(
                        or_(
                            func.lower(PoliticalParty.acronym) == party.lower(),
                            func.lower(PoliticalParty.name).contains(party.lower()),
                        )
                    )
                )
            )

        if state:
            query = query.where(Politician.state_code == state.upper())

        if position:
            query = query.where(
                Politician.current_position_id.in_(
                    select(PoliticalPosition.id).where(
                        func.lower(PoliticalPosition.name).contains(position.lower())
                    )
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Paginate
        offset = (page - 1) * limit
        query = query.order_by(Politician.full_name).offset(offset).limit(limit)

        result = await self.db.execute(query)
        politicians = list(result.scalars().all())

        return politicians, total

    async def get_history(self, politician_id: uuid.UUID) -> list[PoliticianChangeHistory]:
        """Retorna histórico de alterações."""
        result = await self.db.execute(
            select(PoliticianChangeHistory)
            .where(PoliticianChangeHistory.politician_id == politician_id)
            .order_by(PoliticianChangeHistory.created_at.desc())
        )
        return list(result.scalars().all())

    # --- Aliases ---

    async def add_alias(
        self, politician_id: uuid.UUID, alias: str, alias_type: str = "ballot_name",
        source_id: str | None = None,
    ) -> PoliticianAlias:
        record = PoliticianAlias(
            politician_id=politician_id,
            alias=alias,
            normalized_alias=normalize_text(alias),
            alias_type=alias_type,
            source_id=source_id,
        )
        self.db.add(record)
        await self.db.flush()
        return record

    # --- Memberships ---

    async def add_membership(
        self, politician_id: uuid.UUID, party_id: uuid.UUID,
        started_at=None, ended_at=None, state_code: str | None = None,
        is_current: bool = False, source_url: str | None = None,
    ) -> PartyMembership:
        record = PartyMembership(
            politician_id=politician_id,
            party_id=party_id,
            started_at=started_at,
            ended_at=ended_at,
            state_code=state_code,
            is_current=is_current,
            source_url=source_url,
        )
        self.db.add(record)
        await self.db.flush()
        return record

    # --- Mandates ---

    async def add_mandate(
        self, politician_id: uuid.UUID, position_id: uuid.UUID,
        party_id: uuid.UUID | None = None, state_code: str | None = None,
        city_name: str | None = None, started_at=None, ended_at=None,
        status: str = "in_office", source_url: str | None = None,
    ) -> PoliticalMandate:
        record = PoliticalMandate(
            politician_id=politician_id,
            position_id=position_id,
            party_id=party_id,
            state_code=state_code,
            city_name=city_name,
            started_at=started_at,
            ended_at=ended_at,
            status=status,
            source_url=source_url,
        )
        self.db.add(record)
        await self.db.flush()
        return record

    # --- Social Links ---

    async def add_social_link(
        self, politician_id: uuid.UUID, platform: str, url: str,
        username: str | None = None, is_official: bool = False,
    ) -> PoliticianSocialLink:
        record = PoliticianSocialLink(
            politician_id=politician_id,
            platform=platform,
            url=url,
            username=username,
            is_official=is_official,
        )
        self.db.add(record)
        await self.db.flush()
        return record
