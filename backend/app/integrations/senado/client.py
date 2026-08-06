"""Cliente HTTP para a API de Dados Abertos do Senado Federal."""

import asyncio
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.integrations.senado.constants import (
    SENADO_API_BASE,
    SENADO_RATE_LIMIT_PER_MINUTE,
    SENADO_TIMEOUT_SECONDS,
)
from app.integrations.senado.exceptions import SenadoApiError, SenadoRateLimitError

logger = logging.getLogger(__name__)


class SenadoClient:
    """Cliente assíncrono para a API do Senado Federal."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._request_count = 0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=SENADO_API_BASE,
                timeout=SENADO_TIMEOUT_SECONDS,
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
    async def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """GET request com retry."""
        client = await self._get_client()
        self._request_count += 1

        if self._request_count % SENADO_RATE_LIMIT_PER_MINUTE == 0:
            await asyncio.sleep(2)

        try:
            response = await client.get(path, params=params)
            if response.status_code == 429:
                await asyncio.sleep(60)
                raise SenadoRateLimitError()
            if response.status_code >= 400:
                raise SenadoApiError(response.status_code, response.text[:200])
            return response.json()
        except httpx.TimeoutException as e:
            raise SenadoApiError(0, f"Timeout: {e}") from e

    # --- Convenience methods ---

    async def list_current_senators(self) -> list[dict]:
        """Lista senadores em exercício."""
        data = await self.get("/senador/lista/atual")
        # Senado API returns nested structure
        parlamentares = data.get("ListaParlamentarEmExercicio", {})
        return parlamentares.get("Parlamentares", {}).get("Parlamentar", [])

    async def get_senator(self, code: int) -> dict:
        """Detalhes de um senador."""
        data = await self.get(f"/senador/{code}")
        return data.get("DetalheParlamentar", {}).get("Parlamentar", {})

    async def get_senator_mandates(self, code: int) -> list[dict]:
        """Mandatos de um senador."""
        data = await self.get(f"/senador/{code}/mandatos")
        mandatos = data.get("MandatoParlamentar", {})
        return mandatos.get("Parlamentar", {}).get("Mandatos", {}).get("Mandato", [])

    async def get_senator_votes(self, code: int) -> list[dict]:
        """Votações de um senador."""
        data = await self.get(f"/senador/{code}/votacoes")
        votacoes = data.get("VotacaoParlamentar", {})
        return votacoes.get("Parlamentar", {}).get("Votacoes", {}).get("Votacao", [])

    async def list_matters(self, year: int, **filters) -> list[dict]:
        """Lista matérias legislativas."""
        params = {"ano": year, **filters}
        data = await self.get("/materia/pesquisa/lista", params)
        pesquisa = data.get("PesquisaBasicaMateria", {})
        return pesquisa.get("Materias", {}).get("Materia", [])

    async def list_committees(self) -> list[dict]:
        """Lista comissões atuais."""
        data = await self.get("/comissao/lista/atual")
        comissoes = data.get("ListaColegiados", {})
        return comissoes.get("Colegiados", {}).get("Colegiado", [])
