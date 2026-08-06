"""Router principal da API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_integrations,
    admin_politicians,
    admin_rbac,
    auth,
    donations,
    electoral,
    health,
    indicators,
    judicial,
    legislative,
    mfa,
    news,
    politicians,
    promises,
    transparency,
    users,
)

api_router = APIRouter()

# Health checks
api_router.include_router(health.router)

# Autenticação
api_router.include_router(auth.router)
api_router.include_router(mfa.router)

# Usuários
api_router.include_router(users.router)

# Políticos (público)
api_router.include_router(politicians.router)

# Dados eleitorais (público)
api_router.include_router(electoral.router)

# Dados legislativos (público)
api_router.include_router(legislative.router)

# Administração
api_router.include_router(admin_rbac.router)
api_router.include_router(admin_politicians.router)
api_router.include_router(admin_integrations.router)

# Notícias
api_router.include_router(news.router)

# Promessas
api_router.include_router(promises.router)

# Processos judiciais
api_router.include_router(judicial.router)

# Indicadores e rankings
api_router.include_router(indicators.router)

# Doações
api_router.include_router(donations.router)

# Transparência institucional
api_router.include_router(transparency.router)
