"""Cliente Redis compartilhado para a aplicação."""

import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Retorna conexão Redis reutilizável."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _redis_pool


async def close_redis() -> None:
    """Fecha conexão Redis."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None


class RedisStore:
    """Wrapper para operações comuns no Redis."""

    @staticmethod
    async def set_json(
        key: str, value: dict[str, Any], ttl_seconds: int
    ) -> None:
        """Armazena JSON no Redis com TTL."""
        r = await get_redis()
        await r.setex(key, ttl_seconds, json.dumps(value))

    @staticmethod
    async def get_json(key: str) -> dict[str, Any] | None:
        """Lê JSON do Redis. Retorna None se não existir."""
        r = await get_redis()
        data = await r.get(key)
        if data is None:
            return None
        return json.loads(data)

    @staticmethod
    async def delete(key: str) -> None:
        """Remove chave do Redis."""
        r = await get_redis()
        await r.delete(key)

    @staticmethod
    async def exists(key: str) -> bool:
        """Verifica se chave existe."""
        r = await get_redis()
        return bool(await r.exists(key))

    @staticmethod
    async def increment(key: str, ttl_seconds: int | None = None) -> int:
        """Incrementa contador atômico."""
        r = await get_redis()
        val = await r.incr(key)
        if ttl_seconds and val == 1:
            await r.expire(key, ttl_seconds)
        return val
