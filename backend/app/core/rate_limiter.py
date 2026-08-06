"""Rate limiting com Redis para proteção contra abuso."""

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


class RateLimiter:
    """Rate limiter baseado em Redis com sliding window."""

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def is_rate_limited(
        self,
        key: str,
        max_attempts: int,
        window_seconds: int,
    ) -> bool:
        """
        Verifica se a chave excedeu o limite de tentativas na janela.
        Retorna True se limitado (deve bloquear), False se permitido.
        """
        redis = await self._get_redis()
        current = await redis.get(key)
        if current is not None and int(current) >= max_attempts:
            return True
        return False

    async def increment(self, key: str, window_seconds: int) -> int:
        """Incrementa o contador e define TTL se necessário."""
        redis = await self._get_redis()
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        results = await pipe.execute()
        return int(results[0])

    async def reset(self, key: str) -> None:
        """Reseta o contador (ex: após login bem-sucedido)."""
        redis = await self._get_redis()
        await redis.delete(key)

    async def get_remaining(self, key: str, max_attempts: int) -> int:
        """Retorna quantas tentativas restam."""
        redis = await self._get_redis()
        current = await redis.get(key)
        if current is None:
            return max_attempts
        return max(0, max_attempts - int(current))

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None


# Instância singleton
rate_limiter = RateLimiter()


# --- Configurações de rate limiting por rota ---

RATE_LIMITS = {
    "login": {"max_attempts": 5, "window_seconds": 900},  # 5 per 15min
    "register": {"max_attempts": 5, "window_seconds": 3600},  # 5 per hour
    "forgot_password": {"max_attempts": 3, "window_seconds": 3600},  # 3 per hour
    "resend_verification": {"max_attempts": 3, "window_seconds": 3600},  # 3 per hour
    "mfa_verify": {"max_attempts": 5, "window_seconds": 600},  # 5 per 10min
    "refresh": {"max_attempts": 30, "window_seconds": 900},  # 30 per 15min
}


def build_rate_key(route: str, ip: str, identifier: str | None = None) -> str:
    """Constrói chave normalizada para rate limiting."""
    parts = ["rate_limit", route, ip]
    if identifier:
        # Hash do identifier para evitar info leakage no Redis
        import hashlib
        id_hash = hashlib.sha256(identifier.lower().encode()).hexdigest()[:16]
        parts.append(id_hash)
    return ":".join(parts)
