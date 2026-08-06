"""API pública e administrativa de promessas de campanha."""

import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_audit_service,
    get_client_ip,
    get_current_user,
    require_permission,
    require_role,
)
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.politician import Politician
from app.models.promise import (
    CampaignPromise,
    PromiseAssessment,
    PromiseContestation,
    PromiseEvidence,
    PromiseStatusHistory,
)
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.services.audit import AuditService
from app.services.promises import PromiseService

router = APIRouter(tags=["Promessas"])


def _get_promise_service(
    db: AsyncSession = Depends(get_db),
) -> PromiseService:
    return PromiseService(db)


# --- Public endpoints ---

@router.get("/promises")
async def list_promises(
    category: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: PromiseService = Depends(_get_promise_service),
):
    """Lista promessas publicadas (todas)."""
    promises, total = await service.search(
        category=category, status=status, page=page, limit=limit,
    )
    pages = math.ceil(total / limit) if total > 0 else 0

    items = [
        {
            "id": p.id, "title": p.title, "category": p.category,
            "promise_type": p.promise_type, "status": p.status,
            "progress_percentage": p.progress_percentage,
            "competence_status": p.competence_status,
            "published_at": p.published_at.isoformat() if p.published_at else None,
        }
        for p in promises
    ]

    return {"data": items, "pagination": {"total": total, "page": page, "pages": pages}}


@router.get("/promises/{promise_id}")
async def get_promise(
    promise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Detalhes de uma promessa publicada."""
    result = await db.execute(
        select(CampaignPromise).where(
            CampaignPromise.id == promise_id,
            CampaignPromise.editorial_status == "published",
        )
    )
    promise = result.scalar_one_or_none()
    if not promise:
        raise NotFoundError(detail="Promessa não encontrada.")

    return {
        "id": promise.id, "title": promise.title, "description": promise.description,
        "category": promise.category, "promise_type": promise.promise_type,
        "source_excerpt": promise.source_excerpt, "source_page": promise.source_page,
        "source_type": promise.source_type,
        "competence_status": promise.competence_status,
        "target_value": promise.target_value, "target_unit": promise.target_unit,
        "baseline_value": promise.baseline_value, "deadline_text": promise.deadline_text,
        "status": promise.status, "progress_percentage": promise.progress_percentage,
        "current_value": promise.current_value,
        "methodology_version": promise.methodology_version,
        "published_at": promise.published_at.isoformat() if promise.published_at else None,
    }


@router.get("/promises/{promise_id}/evidences")
async def get_promise_evidences(
    promise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Lista evidências de uma promessa."""
    result = await db.execute(
        select(PromiseEvidence).where(PromiseEvidence.promise_id == promise_id)
        .order_by(PromiseEvidence.document_date.desc())
    )
    evidences = result.scalars().all()

    return {
        "data": [
            {
                "id": e.id, "type": e.evidence_type, "title": e.title,
                "description": e.description, "source_url": e.source_url,
                "source_name": e.source_name, "document_date": str(e.document_date) if e.document_date else None,
                "supports_progress": e.supports_progress,
                "contradicts_progress": e.contradicts_progress,
                "value": e.value, "unit": e.unit, "verified": e.verified,
            }
            for e in evidences
        ],
    }


@router.get("/promises/{promise_id}/history")
async def get_promise_history(
    promise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Histórico de status e avaliações."""
    # Status history
    status_result = await db.execute(
        select(PromiseStatusHistory).where(PromiseStatusHistory.promise_id == promise_id)
        .order_by(PromiseStatusHistory.created_at.desc())
    )
    status_changes = status_result.scalars().all()

    # Assessments
    assess_result = await db.execute(
        select(PromiseAssessment).where(PromiseAssessment.promise_id == promise_id)
        .order_by(PromiseAssessment.assessment_date.desc())
    )
    assessments = assess_result.scalars().all()

    return {
        "status_history": [
            {"from": s.from_status, "to": s.to_status, "reason": s.reason,
             "by": s.changed_by, "at": s.created_at.isoformat()}
            for s in status_changes
        ],
        "assessments": [
            {"date": str(a.assessment_date), "status": a.status,
             "progress": a.progress_percentage, "summary": a.summary, "by": a.assessed_by}
            for a in assessments
        ],
    }


@router.get("/promises/methodology")
async def get_methodology():
    """Explica a metodologia de avaliação de promessas."""
    return {
        "methodology": {
            "version": "1.0",
            "description": "Avaliação de promessas de campanha do IFB",
            "principles": [
                "Toda promessa extraída passa por revisão humana antes de publicação",
                "O percentual de cumprimento é calculado com base em evidências documentais",
                "Promessas quantitativas usam meta e valor atual para calcular progresso",
                "Promessas qualitativas usam status textual (não percentual forçado)",
                "A competência do cargo é verificada antes da publicação",
                "O acompanhamento é periódico e versionado",
                "Toda evidência possui fonte verificável",
            ],
            "statuses": {
                "not_started": "Nenhuma ação identificada",
                "in_progress": "Ações em andamento",
                "partially_fulfilled": "Parcialmente cumprida",
                "fulfilled": "Cumprida conforme critérios definidos",
                "not_fulfilled": "Prazo vencido sem cumprimento",
                "blocked": "Impedida por fator externo",
                "cancelled": "Cancelada formalmente",
                "outside_competence": "Fora da competência do cargo",
                "not_verifiable": "Sem dados suficientes para avaliar",
            },
            "source": "Instituto Fiscaliza Brasil",
        },
    }


# --- Politician promises ---

@router.get("/politicians/{slug}/promises")
async def get_politician_promises(
    slug: str,
    category: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: PromiseService = Depends(_get_promise_service),
):
    """Lista promessas publicadas de um político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    promises, total = await service.search(
        politician_id=politician_id, category=category, status=status,
        page=page, limit=limit,
    )

    items = [
        {
            "id": p.id, "title": p.title, "category": p.category,
            "promise_type": p.promise_type, "status": p.status,
            "progress_percentage": p.progress_percentage,
            "target_value": p.target_value, "target_unit": p.target_unit,
            "competence_status": p.competence_status,
        }
        for p in promises
    ]

    return {"data": items, "pagination": {"total": total, "page": page}}


@router.get("/politicians/{slug}/promise-summary")
async def get_politician_promise_summary(
    slug: str,
    db: AsyncSession = Depends(get_db),
    service: PromiseService = Depends(_get_promise_service),
):
    """Resumo de promessas de um político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    summary = await service.get_politician_summary(politician_id)
    return summary


# --- Contestation ---

class PromiseContestRequest(BaseModel):
    reason: str
    description: str | None = None


@router.post("/promises/{promise_id}/contest", response_model=MessageResponse)
async def contest_promise(
    promise_id: uuid.UUID,
    data: PromiseContestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Contesta uma promessa publicada."""
    contestation = PromiseContestation(
        promise_id=promise_id,
        user_id=user.id,
        reason=data.reason,
        description=data.description,
        status="pending",
    )
    db.add(contestation)
    await db.flush()
    return MessageResponse(message="Contestação registrada para análise.")
