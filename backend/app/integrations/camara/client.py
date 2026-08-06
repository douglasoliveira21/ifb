"""Cliente HTTP para a API de Dados Abertos da Câmara dos Deputados."""

import asyncio
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.camara.constants import (
    CAMARA_API_BASE,
    CAMARA_DEFAULT_PAGE_SIZE,
    CAMARA_RATE_LIMIT_PER_MINUTE,
    CAMARA_TIMEOUT_SECONDS,
)
from app.integrations.camara.exceptions import (
    CamaraApiError,
    CamaraRateLimitError,
    CamaraTimeoutError,
)

logger = logging.getLogger(__name__)


class CamaraClient:
    """Cliente assíncrono para a API da Câmara dos Deputados."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._request_count = 0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=CAMARA_API_BASE,
                timeout=CAMARA_TIMEOUT_SECONDS,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "IFB-Platform/1.0 (fiscalizabrasil.org.br)",
                },
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def _request(
        self, method: str, path: str, params: dict | None = None
    ) -> dict[str, Any]:
        """Executa request com retry e rate limiting."""
        client = await self._get_client()
        self._request_count += 1

        # Simple rate limiting (delay between requests)
        if self._request_count % CAMARA_RATE_LIMIT_PER_MINUTE == 0:
            await asyncio.sleep(1.5)

        try:
            response = await client.request(method, path, params=params)

            if response.status_code == 429:
                logger.warning("Câmara rate limit hit. Waiting 60s.")
                await asyncio.sleep(60)
                raise CamaraRateLimitError("Rate limit exceeded")

            if response.status_code >= 500:
                raise CamaraApiError(response.status_code, "Server error")

            if response.status_code >= 400:
                raise CamaraApiError(response.status_code, response.text[:200])

            return response.json()

        except httpx.TimeoutException as e:
            raise CamaraTimeoutError(str(e)) from e
        except httpx.ConnectError as e:
            raise CamaraApiError(0, f"Connection error: {e}") from e

    async def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """GET request."""
        return await self._request("GET", path, params)

    async def get_paginated(
        self,
        path: str,
        params: dict | None = None,
        page_size: int = CAMARA_DEFAULT_PAGE_SIZE,
        max_pages: int = 100,
    ) -> list[dict]:
        """Coleta todos os resultados paginados."""
        all_items = []
        params = params or {}
        params["itens"] = page_size
        page = 1

        while page <= max_pages:
            params["pagina"] = page
            data = await self.get(path, params)

            items = data.get("dados", [])
            if not items:
                break

            all_items.extend(items)

            # Check if there are more pages
            links = data.get("links", [])
            has_next = any(l.get("rel") == "next" for l in links)
            if not has_next:
                break

            page += 1

        return all_items

    # --- Convenience methods ---

    async def list_deputies(
        self, legislature: int | None = None, **filters
    ) -> list[dict]:
        """Lista deputados."""
        params = filters
        if legislature:
            params["idLegislatura"] = legislature
        return await self.get_paginated("/deputados", params)

    async def get_deputy(self, deputy_id: int) -> dict:
        """Detalhes de um deputado."""
        data = await self.get(f"/deputados/{deputy_id}")
        return data.get("dados", {})

    async def get_deputy_expenses(
        self, deputy_id: int, year: int | None = None, month: int | None = None
    ) -> list[dict]:
        """Despesas de um deputado (CEAP)."""
        params = {}
        if year:
            params["ano"] = year
        if month:
            params["mes"] = month
        return await self.get_paginated(f"/deputados/{deputy_id}/despesas", params)

    async def list_propositions(self, **filters) -> list[dict]:
        """Lista proposições."""
        return await self.get_paginated("/proposicoes", filters)

    async def get_proposition(self, prop_id: int) -> dict:
        """Detalhes de uma proposição."""
        data = await self.get(f"/proposicoes/{prop_id}")
        return data.get("dados", {})

    async def get_vote_event(self, vote_id: int) -> dict:
        """Detalhes de uma votação."""
        data = await self.get(f"/votacoes/{vote_id}")
        return data.get("dados", {})

    async def get_vote_voters(self, vote_id: int) -> list[dict]:
        """Votos individuais de uma votação."""
        data = await self.get(f"/votacoes/{vote_id}/votos")
        return data.get("dados", [])
