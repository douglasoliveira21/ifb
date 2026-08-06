"""API pública de processos judiciais."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.judicial import (
    JudicialAppeal,
    JudicialCase,
    JudicialCaseMatch,
    JudicialCaseParty,
    JudicialContestation,
    JudicialDecision,
    JudicialMovement,
)
from app.models.politician import Politician
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from app.schemas.auth import MessageResponse

router = APIRouter(tags=["Processos Judiciais"])

JUDICIAL_DISCLAIMER = (
    "A existência de um processo não implica culpa. As informações exibidas "
    "refletem dados públicos disponíveis na fonte oficial e podem estar sujeitas "
    "a recursos, correções e atualizações."
)


@router.get("/politicians/{slug}/judicial-cases")
async def get_politician_judicial_cases(
    slug: str,
    role: str | None = Query(None),
    status: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista processos judiciais vinculados ao político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    # Find confirmed matches
    query = (
        select(JudicialCase, JudicialCaseParty)
        .join(JudicialCaseParty, JudicialCaseParty.case_id == JudicialCase.id)
        .where(
            JudicialCaseParty.politician_id == politician_id,
            JudicialCaseParty.match_status == "confirmed",
            JudicialCase.editorial_status == "published",
            JudicialCase.public_access == True,
        )
    )
    if role:
        query = query.where(JudicialCaseParty.role_normalized == role)
    if status:
        query = query.where(JudicialCase.procedural_status == status)
    if category:
        query = query.where(JudicialCase.case_category == category)

    query = query.order_by(desc(JudicialCase.last_movement_date))
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        {
            "id": case.id,
            "tribunal": case.tribunal,
            "case_class": case.case_class_name,
            "instance": case.instance,
            "filing_date": str(case.filing_date) if case.filing_date else None,
            "last_movement_date": str(case.last_movement_date) if case.last_movement_date else None,
            "politician_role": party.role_normalized,
            "politician_role_original": party.role_original,
            "procedural_status": case.procedural_status,
            "normalized_status": case.normalized_status,
            "case_category": case.case_category,
            "source_url": case.source_url,
        }
        for case, party in rows
    ]

    return {
        "data": items,
        "pagination": {"page": page, "limit": limit},
        "metadata": {
            "source": "Fontes judiciais públicas oficiais",
            "methodology_url": "/api/v1/judicial-cases/methodology",
        },
        "disclaimer": JUDICIAL_DISCLAIMER,
    }


@router.get("/politicians/{slug}/judicial-summary")
async def get_politician_judicial_summary(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Resumo de processos do político com contexto."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    # Count published cases by role
    base = (
        select(JudicialCaseParty.role_normalized, func.count(JudicialCaseParty.id))
        .join(JudicialCase, JudicialCaseParty.case_id == JudicialCase.id)
        .where(
            JudicialCaseParty.politician_id == politician_id,
            JudicialCaseParty.match_status == "confirmed",
            JudicialCase.editorial_status == "published",
        )
        .group_by(JudicialCaseParty.role_normalized)
    )
    role_counts = dict((await db.execute(base)).all())

    # Count by procedural status
    status_base = (
        select(JudicialCase.procedural_status, func.count(JudicialCase.id))
        .join(JudicialCaseParty, JudicialCaseParty.case_id == JudicialCase.id)
        .where(
            JudicialCaseParty.politician_id == politician_id,
            JudicialCaseParty.match_status == "confirmed",
            JudicialCase.editorial_status == "published",
        )
        .group_by(JudicialCase.procedural_status)
    )
    status_counts = dict((await db.execute(status_base)).all())

    total = sum(role_counts.values())

    return {
        "total_confirmed_cases": total,
        "by_role": role_counts,
        "by_status": status_counts,
        "methodology_url": "/api/v1/judicial-cases/methodology",
        "disclaimer": JUDICIAL_DISCLAIMER,
    }


@router.get("/judicial-cases/methodology")
async def get_judicial_methodology():
    """Metodologia de apresentação de processos judiciais."""
    return {
        "version": "1.0",
        "principles": [
            "A existência de processo NÃO implica culpa",
            "Investigação NÃO equivale a condenação",
            "Denúncia aceita torna o político réu, mas não condenado",
            "Condenação em primeira instância pode ser recorrida",
            "Somente condenação transitada em julgado é definitiva",
            "Absolvição posterior atualiza o destaque público",
            "O papel do político no processo é sempre informado",
            "Processos sigilosos não são publicados",
            "Toda publicação passa por revisão humana",
        ],
        "roles_explained": {
            "plaintiff": "O político é autor da ação",
            "defendant": "O político é réu",
            "investigated": "O político está sendo investigado",
            "accused": "O político foi denunciado",
            "appellant": "O político recorreu de decisão",
            "appellee": "O político é parte recorrida",
            "interested_party": "O político é parte interessada",
            "victim": "O político é vítima",
            "other": "Outro tipo de participação",
        },
        "statuses_explained": {
            "active": "Processo em andamento",
            "suspended": "Processo suspenso",
            "archived": "Processo arquivado",
            "closed": "Processo encerrado",
            "on_appeal": "Em fase de recurso",
            "awaiting_decision": "Aguardando decisão",
        },
    }


# --- Contestation ---

class JudicialContestRequest(BaseModel):
    reason: str
    description: str | None = None


@router.post("/judicial-cases/{case_id}/contest", response_model=MessageResponse)
async def contest_judicial_case(
    case_id: uuid.UUID,
    data: JudicialContestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Contesta informação de um processo judicial."""
    contestation = JudicialContestation(
        case_id=case_id,
        user_id=user.id,
        reason=data.reason,
        description=data.description,
        status="pending",
    )
    db.add(contestation)
    await db.flush()
    return MessageResponse(message="Contestação registrada. Será analisada pela equipe.")
