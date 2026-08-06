"""Ponto de entrada da aplicação FastAPI — Instituto Fiscaliza Brasil."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.middleware.correlation import CorrelationIdMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle events da aplicação."""
    # Startup
    if settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.app_env)
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Plataforma pública e apartidária que transforma dados públicos "
            "em informações claras e rastreáveis sobre políticos brasileiros."
        ),
        version="0.1.0",
        docs_url="/api/docs" if settings.app_env != "production" else None,
        redoc_url="/api/redoc" if settings.app_env != "production" else None,
        openapi_url="/api/openapi.json" if settings.app_env != "production" else None,
        lifespan=lifespan,
    )

    # Middlewares
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )

    # Rotas
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
