"""Serviço de conciliação político IFB × parlamentar externo."""

import logging
import unicodedata
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislative import Legislator, PoliticianLegislativeProfile
from app.models.politician import Politician, PoliticianAlias

logger = logging.getLogger(__name__)

# Scoring weights (configurable)
SCORE_OFFICIAL_ID = 100
SCORE_CPF_HASH = 100
SCORE_CANDIDACY_LINK = 90
SCORE_FULL_NAME = 40
SCORE_BIRTH_DATE = 30
SCORE_STATE = 15
SCORE_PARTY = 10
SCORE_POSITION = 10
SCORE_PARLIAMENTARY_NAME = 20

# Penalties
PENALTY_STATE_DIVERGENT = -40
PENALTY_BIRTH_DIVERGENT = -80
PENALTY_POSITION_INCOMPATIBLE = -30
PENALTY_PARTY_DIVERGENT = -15

# Thresholds
THRESHOLD_CONFIRMED = 90
THRESHOLD_PROBABLE = 70


def _normalize(text: str) -> str:
    """Normaliza texto para comparação."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


class ReconciliationResult:
    """Resultado de uma tentativa de conciliação."""

    def __init__(self, politician_id: uuid.UUID | None, score: float, method: str, status: str):
        self.politician_id = politician_id
        self.score = score
        self.method = method
        self.status = status


class LegislativeReconciliationService:
    """Concilia parlamentares com políticos do IFB."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def reconcile_legislator(self, legislator: Legislator) -> ReconciliationResult:
        """
        Tenta vincular um legislator a um politician existente.
        Retorna resultado com score e status.
        """
        # 1. Try exact match by name + state
        candidates = await self._find_candidates(legislator)

        if not candidates:
            return ReconciliationResult(None, 0, "no_match", "pending_review")

        # 2. Score each candidate
        best_match = None
        best_score = 0.0

        for politician in candidates:
            score = self._calculate_score(legislator, politician)
            if score > best_score:
                best_score = score
                best_match = politician

        if not best_match:
            return ReconciliationResult(None, 0, "no_match", "pending_review")

        # 3. Determine status based on threshold
        if best_score >= THRESHOLD_CONFIRMED:
            status = "confirmed"
            method = "auto_confirmed"
        elif best_score >= THRESHOLD_PROBABLE:
            status = "probable"
            method = "auto_probable"
        else:
            status = "pending_review"
            method = "low_confidence"

        return ReconciliationResult(best_match.id, best_score, method, status)

    async def _find_candidates(self, legislator: Legislator) -> list[Politician]:
        """Busca políticos candidatos para conciliação."""
        name_normalized = _normalize(legislator.full_name)

        # Search by name similarity
        query = select(Politician).where(
            Politician.deleted_at == None,
            func.lower(Politician.full_name).contains(name_normalized[:20]),
        )

        if legislator.state_code:
            # Prefer same state but don't exclude
            pass

        result = await self.db.execute(query.limit(20))
        politicians = list(result.scalars().all())

        # Also search aliases
        alias_query = select(Politician).join(
            PoliticianAlias, PoliticianAlias.politician_id == Politician.id
        ).where(
            PoliticianAlias.normalized_alias.contains(name_normalized[:15]),
            Politician.deleted_at == None,
        )
        alias_result = await self.db.execute(alias_query.limit(10))
        alias_politicians = list(alias_result.scalars().all())

        # Merge and dedupe
        seen_ids = {p.id for p in politicians}
        for p in alias_politicians:
            if p.id not in seen_ids:
                politicians.append(p)
                seen_ids.add(p.id)

        return politicians

    def _calculate_score(self, legislator: Legislator, politician: Politician) -> float:
        """Calcula score de similaridade entre legislator e politician."""
        score = 0.0

        # Full name match
        leg_name = _normalize(legislator.full_name)
        pol_name = _normalize(politician.full_name)
        if leg_name == pol_name:
            score += SCORE_FULL_NAME
        elif leg_name in pol_name or pol_name in leg_name:
            score += SCORE_FULL_NAME * 0.6

        # Ballot name / parliamentary name
        if politician.ballot_name:
            pol_ballot = _normalize(politician.ballot_name)
            leg_short = _normalize(legislator.full_name)
            if pol_ballot == leg_short or pol_ballot in leg_short:
                score += SCORE_PARLIAMENTARY_NAME

        # State match
        if legislator.state_code and politician.state_code:
            if legislator.state_code == politician.state_code:
                score += SCORE_STATE
            else:
                score += PENALTY_STATE_DIVERGENT

        # Party match
        if legislator.party_acronym and politician.current_party:
            # Need to check current party
            pass  # Would require party relationship loaded

        # Birth date (if available on both)
        if legislator.birth_date and politician.birth_date:
            if legislator.birth_date == politician.birth_date:
                score += SCORE_BIRTH_DATE
            else:
                score += PENALTY_BIRTH_DIVERGENT

        return score

    async def create_profile(
        self, legislator_id: uuid.UUID, result: ReconciliationResult, house_id: uuid.UUID
    ) -> PoliticianLegislativeProfile | None:
        """Cria ou atualiza o vínculo politician ↔ legislator."""
        if not result.politician_id:
            return None

        # Check existing
        existing = await self.db.execute(
            select(PoliticianLegislativeProfile).where(
                PoliticianLegislativeProfile.legislator_id == legislator_id,
            )
        )
        profile = existing.scalar_one_or_none()

        if profile:
            profile.politician_id = result.politician_id
            profile.match_method = result.method
            profile.match_confidence = result.score
            profile.status = result.status
        else:
            profile = PoliticianLegislativeProfile(
                politician_id=result.politician_id,
                legislator_id=legislator_id,
                house_id=house_id,
                match_method=result.method,
                match_confidence=result.score,
                status=result.status,
            )
            self.db.add(profile)

        await self.db.flush()
        return profile

    async def reconcile_all_pending(self, house_id: uuid.UUID) -> dict:
        """Reconcilia todos os legisladores sem vínculo."""
        # Find unlinked legislators
        linked_ids = select(PoliticianLegislativeProfile.legislator_id)
        result = await self.db.execute(
            select(Legislator).where(
                Legislator.house_id == house_id,
                Legislator.id.not_in(linked_ids),
            )
        )
        unlinked = result.scalars().all()

        stats = {"total": len(unlinked), "confirmed": 0, "probable": 0, "pending": 0, "no_match": 0}

        for legislator in unlinked:
            rec_result = await self.reconcile_legislator(legislator)
            if rec_result.politician_id:
                await self.create_profile(legislator.id, rec_result, house_id)
                if rec_result.status == "confirmed":
                    stats["confirmed"] += 1
                elif rec_result.status == "probable":
                    stats["probable"] += 1
                else:
                    stats["pending"] += 1
            else:
                stats["no_match"] += 1

        await self.db.flush()
        return stats
