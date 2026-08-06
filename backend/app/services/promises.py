"""Serviço de gestão de promessas de campanha."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.promise import (
    CampaignPromise,
    PromiseAssessment,
    PromiseContestation,
    PromiseEvidence,
    PromiseExtractionJob,
    PromiseStatusHistory,
)

logger = logging.getLogger(__name__)

# Valid promise statuses
PROMISE_STATUSES = {
    "not_started", "in_progress", "partially_fulfilled",
    "fulfilled", "not_fulfilled", "blocked", "cancelled",
    "outside_competence", "not_verifiable", "under_review",
}

# Valid editorial statuses
EDITORIAL_STATUSES = {
    "draft", "review_pending", "published",
    "contested", "suspended", "archived",
}

# Competence check mapping
COMPETENCE_RULES = {
    "federal_executive": {"health", "education", "economy", "infrastructure", "public_security"},
    "state_executive": {"health", "education", "public_security", "transport", "infrastructure"},
    "municipal_executive": {"health", "education", "transport", "sanitation", "housing", "urban"},
    "federal_legislative": {"legislation", "oversight", "budget_amendments"},
    "state_legislative": {"legislation", "oversight"},
    "municipal_legislative": {"legislation", "oversight"},
}


class PromiseService:
    """Gerencia promessas de campanha, evidências e avaliações."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_promise(
        self,
        politician_id: uuid.UUID,
        title: str,
        category: str,
        created_by: str,
        **kwargs,
    ) -> CampaignPromise:
        """Cria promessa (status: draft, editorial: review_pending)."""
        promise = CampaignPromise(
            politician_id=politician_id,
            title=title.strip(),
            category=category,
            status="not_started",
            editorial_status="draft",
            **kwargs,
        )
        self.db.add(promise)
        await self.db.flush()

        # History
        self.db.add(PromiseStatusHistory(
            promise_id=promise.id,
            to_status="not_started",
            reason="Promise created",
            changed_by=created_by,
        ))
        await self.db.flush()
        return promise

    async def update_status(
        self,
        promise_id: uuid.UUID,
        new_status: str,
        changed_by: str,
        reason: str | None = None,
        progress: float | None = None,
        current_value: float | None = None,
    ) -> CampaignPromise:
        """Atualiza status de uma promessa com histórico."""
        if new_status not in PROMISE_STATUSES:
            raise ValidationError(detail=f"Status inválido: {new_status}")

        result = await self.db.execute(
            select(CampaignPromise).where(CampaignPromise.id == promise_id)
        )
        promise = result.scalar_one_or_none()
        if not promise:
            raise NotFoundError(detail="Promessa não encontrada.")

        old_status = promise.status
        promise.status = new_status
        if progress is not None:
            promise.progress_percentage = progress
        if current_value is not None:
            promise.current_value = current_value
        promise.version += 1

        self.db.add(PromiseStatusHistory(
            promise_id=promise.id,
            from_status=old_status,
            to_status=new_status,
            reason=reason,
            changed_by=changed_by,
        ))
        await self.db.flush()
        return promise

    async def publish(self, promise_id: uuid.UUID, published_by: str) -> None:
        """Publica promessa após revisão."""
        result = await self.db.execute(
            select(CampaignPromise).where(CampaignPromise.id == promise_id)
        )
        promise = result.scalar_one_or_none()
        if not promise:
            raise NotFoundError(detail="Promessa não encontrada.")

        if promise.editorial_status == "published":
            return

        promise.editorial_status = "published"
        promise.published_at = datetime.now(UTC)
        await self.db.flush()

    async def add_evidence(
        self,
        promise_id: uuid.UUID,
        evidence_type: str,
        title: str,
        added_by: str,
        **kwargs,
    ) -> PromiseEvidence:
        """Adiciona evidência a uma promessa."""
        evidence = PromiseEvidence(
            promise_id=promise_id,
            evidence_type=evidence_type,
            title=title,
            **kwargs,
        )
        self.db.add(evidence)
        await self.db.flush()
        return evidence

    async def create_assessment(
        self,
        promise_id: uuid.UUID,
        status: str,
        assessed_by: str,
        progress_percentage: float | None = None,
        summary: str | None = None,
    ) -> PromiseAssessment:
        """Cria avaliação periódica de uma promessa."""
        assessment = PromiseAssessment(
            promise_id=promise_id,
            assessment_date=datetime.now(UTC),
            status=status,
            progress_percentage=progress_percentage,
            summary=summary,
            assessed_by=assessed_by,
        )
        self.db.add(assessment)

        # Update promise status to match latest assessment
        result = await self.db.execute(
            select(CampaignPromise).where(CampaignPromise.id == promise_id)
        )
        promise = result.scalar_one_or_none()
        if promise:
            promise.status = status
            if progress_percentage is not None:
                promise.progress_percentage = progress_percentage

        await self.db.flush()
        return assessment

    async def get_politician_summary(self, politician_id: uuid.UUID) -> dict:
        """Resumo de promessas de um político."""
        base_query = select(CampaignPromise).where(
            CampaignPromise.politician_id == politician_id,
            CampaignPromise.editorial_status == "published",
        )

        total = (await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )).scalar_one()

        # Count by status
        counts = {}
        for status in ["fulfilled", "partially_fulfilled", "in_progress",
                       "not_started", "not_fulfilled", "not_verifiable"]:
            q = select(func.count(CampaignPromise.id)).where(
                CampaignPromise.politician_id == politician_id,
                CampaignPromise.editorial_status == "published",
                CampaignPromise.status == status,
            )
            counts[status] = (await self.db.execute(q)).scalar_one()

        return {
            "total_promises": total,
            **counts,
            "overall_percentage": None,  # Not forced without methodology
            "methodology_url": "/api/v1/promises/methodology",
        }

    async def search(
        self,
        politician_id: uuid.UUID | None = None,
        category: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[CampaignPromise], int]:
        """Pesquisa promessas publicadas."""
        query = select(CampaignPromise).where(
            CampaignPromise.editorial_status == "published"
        )
        if politician_id:
            query = query.where(CampaignPromise.politician_id == politician_id)
        if category:
            query = query.where(CampaignPromise.category == category)
        if status:
            query = query.where(CampaignPromise.status == status)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_q)).scalar_one()

        query = query.order_by(CampaignPromise.created_at.desc())
        result = await self.db.execute(query.offset((page - 1) * limit).limit(limit))

        return list(result.scalars().all()), total
