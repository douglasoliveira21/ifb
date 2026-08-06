"""Schemas de resposta dos health checks."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Resposta do health check principal."""

    status: str
    version: str
    environment: str


class HealthDetailResponse(BaseModel):
    """Resposta detalhada com status de dependências."""

    status: str
    version: str
    environment: str
    database: str
    redis: str
