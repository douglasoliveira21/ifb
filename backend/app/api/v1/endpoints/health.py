"""Endpoints de health check."""

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.health import HealthDetailResponse, HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check básico - retorna status da aplicação."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
    )


@router.get("/health/detailed", response_model=HealthDetailResponse)
async def health_check_detailed(
    db: AsyncSession = Depends(get_db),
) -> HealthDetailResponse:
    """Health check detalhado - verifica banco e Redis."""
    # Verificar PostgreSQL
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Verificar Redis
    redis_status = "healthy"
    try:
        redis_client = aioredis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.aclose()
    except Exception:
        redis_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"

    return HealthDetailResponse(
        status=overall,
        version="0.1.0",
        environment=settings.app_env,
        database=db_status,
        redis=redis_status,
    )
