"""API pública de indicadores e rankings."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.indicator import (
    IndicatorContestation,
    IndicatorDefinition,
    IndicatorMethodology,
    IndicatorResult,
    RankingView,
)
from app.models.politician import Politician
from app.models.user import User
from app.api.v1.dependencies import get_current_user
from app.schemas.auth import MessageResponse

router = APIRouter(tags=["Indicadores e Rankings"])


@router.get("/indicators")
async def list_indicators(db: AsyncSession = Depends(get_db)):
    """Lista indicadores públicos ativos."""
    result = await db.execute(
        select(IndicatorDefinition).where(
            IndicatorDefinition.active == True, IndicatorDefinition.public == True
        )
    )
    indicators = result.scalars().all()
    return {
        "data": [
            {
                "code": i.code, "name": i.name, "description": i.description,
                "category": i.category, "value_type": i.value_type,
                "higher_is_better": i.higher_is_better,
            }
            for i in indicators
        ]
    }


@router.get("/indicators/{code}")
async def get_indicator(code: str, db: AsyncSession = Depends(get_db)):
    """Detalhes de um indicador."""
    result = await db.execute(
        select(IndicatorDefinition).where(IndicatorDefinition.code == code)
    )
    ind = result.scalar_one_or_none()
    if not ind:
        raise NotFoundError(detail="Indicador não encontrado.")
    return {
        "code": ind.code, "name": ind.name, "description": ind.description,
        "category": ind.category, "value_type": ind.value_type,
        "minimum_value": ind.minimum_value, "maximum_value": ind.maximum_value,
        "higher_is_better": ind.higher_is_better,
    }


@router.get("/indicators/{code}/methodology")
async def get_indicator_methodology(code: str, db: AsyncSession = Depends(get_db)):
    """Metodologia publicada de um indicador."""
    ind_result = await db.execute(
        select(IndicatorDefinition).where(IndicatorDefinition.code == code)
    )
    ind = ind_result.scalar_one_or_none()
    if not ind:
        raise NotFoundError(detail="Indicador não encontrado.")

    meth_result = await db.execute(
        select(IndicatorMethodology).where(
            IndicatorMethodology.indicator_id == ind.id,
            IndicatorMethodology.status == "published",
        ).order_by(desc(IndicatorMethodology.effective_from)).limit(1)
    )
    meth = meth_result.scalar_one_or_none()
    if not meth:
        return {"message": "Metodologia ainda não publicada para este indicador."}

    return {
        "indicator": ind.code,
        "version": meth.version,
        "name": meth.name,
        "description": meth.description,
        "formula": meth.formula,
        "minimum_data_requirements": meth.minimum_data_requirements,
        "limitations": meth.limitations,
        "effective_from": str(meth.effective_from) if meth.effective_from else None,
        "published_at": meth.published_at.isoformat() if meth.published_at else None,
    }


# --- Politician indicators ---

@router.get("/politicians/{slug}/indicators")
async def get_politician_indicators(
    slug: str, db: AsyncSession = Depends(get_db)
):
    """Todos os indicadores calculados de um político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    # Get latest result per indicator
    results = await db.execute(
        select(IndicatorResult, IndicatorDefinition)
        .join(IndicatorDefinition, IndicatorResult.indicator_id == IndicatorDefinition.id)
        .where(IndicatorResult.politician_id == politician_id)
        .order_by(IndicatorResult.calculated_at.desc())
    )
    rows = results.all()

    # Dedupe: keep latest per indicator
    seen = set()
    items = []
    for result, definition in rows:
        if definition.code in seen:
            continue
        seen.add(definition.code)
        items.append({
            "indicator_code": definition.code,
            "indicator_name": definition.name,
            "category": definition.category,
            "value": result.value,
            "value_type": definition.value_type,
            "status": result.status,
            "period_start": str(result.period_start) if result.period_start else None,
            "period_end": str(result.period_end) if result.period_end else None,
            "explanation": result.explanation,
            "limitations": result.limitations_json,
            "calculated_at": result.calculated_at.isoformat(),
        })

    return {
        "data": items,
        "disclaimer": "Indicadores calculados com base em dados públicos e metodologia documentada.",
    }


@router.get("/politicians/{slug}/indicators/{code}")
async def get_politician_indicator_detail(
    slug: str, code: str, db: AsyncSession = Depends(get_db)
):
    """Detalhes de um indicador para um político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    ind_result = await db.execute(
        select(IndicatorDefinition).where(IndicatorDefinition.code == code)
    )
    indicator = ind_result.scalar_one_or_none()
    if not indicator:
        raise NotFoundError(detail="Indicador não encontrado.")

    result = await db.execute(
        select(IndicatorResult).where(
            IndicatorResult.politician_id == politician_id,
            IndicatorResult.indicator_id == indicator.id,
        ).order_by(desc(IndicatorResult.calculated_at)).limit(1)
    )
    calc = result.scalar_one_or_none()
    if not calc:
        return {"status": "not_calculated", "message": "Indicador ainda não calculado."}

    return {
        "indicator": code,
        "value": calc.value,
        "status": calc.status,
        "period": {"start": str(calc.period_start), "end": str(calc.period_end)},
        "inputs": calc.inputs_json,
        "explanation": calc.explanation,
        "limitations": calc.limitations_json,
        "sources": calc.sources_json,
        "methodology_url": f"/api/v1/indicators/{code}/methodology",
        "calculated_at": calc.calculated_at.isoformat(),
    }


# --- Rankings ---

@router.get("/rankings")
async def list_rankings(db: AsyncSession = Depends(get_db)):
    """Lista rankings públicos disponíveis."""
    result = await db.execute(
        select(RankingView).where(RankingView.public == True)
    )
    rankings = result.scalars().all()
    return {
        "data": [
            {
                "code": r.code, "name": r.name, "description": r.description,
                "scope_position": r.scope_position, "scope_house": r.scope_house,
                "entries_count": r.entries_count, "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in rankings
        ],
        "disclaimer": (
            "Rankings são organizados por dimensão individual. "
            "Não há nota geral que consolide todas as dimensões."
        ),
    }


# --- Contestation ---

from pydantic import BaseModel


class IndicatorContestRequest(BaseModel):
    reason: str
    description: str | None = None


@router.post("/indicator-results/{result_id}/contest", response_model=MessageResponse)
async def contest_indicator_result(
    result_id: uuid.UUID,
    data: IndicatorContestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Contesta resultado de indicador."""
    contestation = IndicatorContestation(
        result_id=result_id,
        user_id=user.id,
        reason=data.reason,
        description=data.description,
        status="pending",
    )
    db.add(contestation)
    await db.flush()
    return MessageResponse(message="Contestação registrada para análise.")
