"""Endpoints administrativos de integrações (TSE, Câmara, Senado)."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_audit_service,
    get_client_ip,
    require_role,
)
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.legislative import (
    Legislator,
    LegislativeHouse,
    PoliticianLegislativeProfile,
    SyncCheckpoint,
)
from app.models.sync import SyncJob
from app.models.user import User
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/admin/integrations", tags=["Admin Integrações"])


# --- Schemas ---

class JobResponse(BaseModel):
    id: uuid.UUID
    provider: str
    resource: str
    scope: str | None
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    total_records: int
    processed_records: int
    created_records: int
    error_records: int
    error_message: str | None


class DashboardResponse(BaseModel):
    total_jobs: int
    running_jobs: int
    failed_jobs_24h: int
    pending_reconciliations: int
    last_sync_camara: datetime | None
    last_sync_senado: datetime | None
    last_sync_tse: datetime | None
    total_legislators: int
    total_linked: int


class SyncRequest(BaseModel):
    resource: str | None = None
    year: int | None = None
    state_code: str | None = None


# --- Endpoints ---

@router.get("/dashboard", response_model=DashboardResponse)
async def get_integration_dashboard(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Dashboard de integrações."""
    # Total jobs
    total_jobs = (await db.execute(select(func.count(SyncJob.id)))).scalar_one()
    running_jobs = (await db.execute(
        select(func.count(SyncJob.id)).where(SyncJob.status == "running")
    )).scalar_one()
    failed_24h = (await db.execute(
        select(func.count(SyncJob.id)).where(
            SyncJob.status == "failed",
            SyncJob.finished_at >= datetime.now(UTC).replace(hour=0, minute=0),
        )
    )).scalar_one()

    # Reconciliation pending
    pending_recon = (await db.execute(
        select(func.count(PoliticianLegislativeProfile.id)).where(
            PoliticianLegislativeProfile.status == "pending_review"
        )
    )).scalar_one()

    # Last syncs
    async def _last_sync(provider: str):
        result = await db.execute(
            select(SyncCheckpoint.last_success_at).where(SyncCheckpoint.provider == provider)
            .order_by(SyncCheckpoint.last_success_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    # Legislators count
    total_legs = (await db.execute(select(func.count(Legislator.id)))).scalar_one()
    total_linked = (await db.execute(
        select(func.count(PoliticianLegislativeProfile.id)).where(
            PoliticianLegislativeProfile.status.in_(["confirmed", "probable"])
        )
    )).scalar_one()

    return DashboardResponse(
        total_jobs=total_jobs,
        running_jobs=running_jobs,
        failed_jobs_24h=failed_24h,
        pending_reconciliations=pending_recon,
        last_sync_camara=await _last_sync("camara"),
        last_sync_senado=await _last_sync("senado"),
        last_sync_tse=await _last_sync("tse"),
        total_legislators=total_legs,
        total_linked=total_linked,
    )


@router.get("/jobs")
async def list_jobs(
    provider: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Lista jobs de sincronização."""
    query = select(SyncJob)
    if provider:
        query = query.where(SyncJob.provider == provider)
    if status:
        query = query.where(SyncJob.status == status)
    query = query.order_by(desc(SyncJob.created_at))

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    jobs = result.scalars().all()

    return {
        "data": [
            JobResponse(
                id=j.id, provider=j.provider, resource=j.resource,
                scope=j.scope, status=j.status, started_at=j.started_at,
                finished_at=j.finished_at, total_records=j.total_records,
                processed_records=j.processed_records, created_records=j.created_records,
                error_records=j.error_records, error_message=j.error_message,
            )
            for j in jobs
        ],
        "page": page,
        "limit": limit,
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Detalhes de um job."""
    result = await db.execute(select(SyncJob).where(SyncJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundError(detail="Job não encontrado.")
    return JobResponse(
        id=job.id, provider=job.provider, resource=job.resource,
        scope=job.scope, status=job.status, started_at=job.started_at,
        finished_at=job.finished_at, total_records=job.total_records,
        processed_records=job.processed_records, created_records=job.created_records,
        error_records=job.error_records, error_message=job.error_message,
    )


@router.post("/jobs/{job_id}/cancel", response_model=MessageResponse)
async def cancel_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Solicita cancelamento de job."""
    result = await db.execute(select(SyncJob).where(SyncJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundError(detail="Job não encontrado.")
    job.status = "cancel_requested"
    await db.flush()
    return MessageResponse(message="Cancelamento solicitado.")


@router.post("/camara/sync", response_model=MessageResponse)
async def trigger_camara_sync(
    data: SyncRequest,
    _user: User = Depends(require_role("admin")),
):
    """Inicia sincronização da Câmara."""
    from app.integrations.camara.tasks import task_sync_deputies
    task_sync_deputies.delay()
    return MessageResponse(message="Sincronização da Câmara iniciada.")


@router.post("/senado/sync", response_model=MessageResponse)
async def trigger_senado_sync(
    data: SyncRequest,
    _user: User = Depends(require_role("admin")),
):
    """Inicia sincronização do Senado."""
    from app.integrations.senado.tasks import task_sync_senators
    task_sync_senators.delay()
    return MessageResponse(message="Sincronização do Senado iniciada.")


@router.post("/tse/sync", response_model=MessageResponse)
async def trigger_tse_sync(
    data: SyncRequest,
    _user: User = Depends(require_role("admin")),
):
    """Inicia sincronização do TSE."""
    return MessageResponse(message="Sincronização TSE requer arquivo. Use a interface de datasets.")


# --- Reconciliation ---

@router.get("/reconciliation")
async def list_reconciliation_queue(
    status: str = Query("pending_review"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Lista fila de conciliação."""
    query = (
        select(PoliticianLegislativeProfile, Legislator)
        .join(Legislator, PoliticianLegislativeProfile.legislator_id == Legislator.id)
        .where(PoliticianLegislativeProfile.status == status)
        .order_by(PoliticianLegislativeProfile.match_confidence.desc())
    )
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        {
            "id": profile.id,
            "legislator_name": leg.full_name,
            "legislator_party": leg.party_acronym,
            "legislator_state": leg.state_code,
            "politician_id": str(profile.politician_id) if profile.politician_id else None,
            "confidence": profile.match_confidence,
            "method": profile.match_method,
            "status": profile.status,
        }
        for profile, leg in rows
    ]

    return {"data": items, "page": page, "limit": limit}


@router.post("/reconciliation/{profile_id}/confirm", response_model=MessageResponse)
async def confirm_reconciliation(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Confirma vínculo político ↔ parlamentar."""
    result = await db.execute(
        select(PoliticianLegislativeProfile).where(PoliticianLegislativeProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError(detail="Perfil não encontrado.")
    profile.status = "confirmed"
    profile.reviewed_by = user.email
    profile.reviewed_at = datetime.now(UTC)
    await db.flush()
    return MessageResponse(message="Vínculo confirmado.")


@router.post("/reconciliation/{profile_id}/reject", response_model=MessageResponse)
async def reject_reconciliation(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Rejeita vínculo."""
    result = await db.execute(
        select(PoliticianLegislativeProfile).where(PoliticianLegislativeProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError(detail="Perfil não encontrado.")
    profile.status = "rejected"
    profile.reviewed_by = user.email
    profile.reviewed_at = datetime.now(UTC)
    await db.flush()
    return MessageResponse(message="Vínculo rejeitado.")
