"""Have I Been Pwned — Password Range API (k-anonymity model)."""

import hashlib
import logging

import httpx

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

HIBP_API_URL = "https://api.pwnedpasswords.com/range/"


async def is_password_compromised(password: str) -> bool | None:
    """
    Verifica se a senha está em bases de dados comprometidas.
    Usa k-anonymity: envia apenas 5 primeiros chars do SHA-1 hash.
    Retorna: True (comprometida), False (segura), None (indisponível).
    """
    if not settings.hibp_enabled:
        return None

    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        async with httpx.AsyncClient(timeout=settings.hibp_timeout_seconds) as client:
            response = await client.get(
                f"{HIBP_API_URL}{prefix}",
                headers={"User-Agent": "IFB-Platform/1.0"},
            )
            if response.status_code != 200:
                logger.warning("HIBP API returned status %d", response.status_code)
                return None

            # Check if our suffix is in the response
            for line in response.text.splitlines():
                parts = line.split(":")
                if len(parts) == 2 and parts[0] == suffix:
                    count = int(parts[1])
                    logger.info("Password found in %d breaches", count)
                    return True

            return False

    except (httpx.TimeoutException, httpx.ConnectError) as e:
        logger.warning("HIBP API unavailable: %s", str(e))
        return None
    except Exception as e:
        logger.error("HIBP unexpected error: %s", str(e))
        return None
