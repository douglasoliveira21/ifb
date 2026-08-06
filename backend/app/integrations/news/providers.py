"""Provedores de notícias — adaptadores independentes."""

import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class NewsProvider(ABC):
    """Interface base para provedores de notícias."""

    provider_name: str = ""

    @abstractmethod
    async def search(
        self,
        query: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        language: str = "pt",
        max_results: int = 50,
    ) -> list[dict]:
        """Busca notícias. Retorna lista normalizada."""
        ...


class GdeltProvider(NewsProvider):
    """Provedor GDELT (gratuito, sem chave)."""

    provider_name = "gdelt"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=15))
    async def search(
        self,
        query: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        language: str = "pt",
        max_results: int = 50,
    ) -> list[dict]:
        params = {
            "query": query,
            "mode": "ArtList",
            "maxrecords": str(min(max_results, 250)),
            "format": "json",
            "sourcelang": language,
            "sort": "DateDesc",
        }
        if start_date:
            params["startdatetime"] = start_date.strftime("%Y%m%d%H%M%S")
        if end_date:
            params["enddatetime"] = end_date.strftime("%Y%m%d%H%M%S")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params=params,
            )
            if response.status_code != 200:
                logger.warning("GDELT returned %d", response.status_code)
                return []

            data = response.json()
            articles = data.get("articles", [])

            return [
                {
                    "provider": "gdelt",
                    "external_id": self._generate_id(a.get("url", "")),
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "image_url": a.get("socialimage"),
                    "source_domain": a.get("domain"),
                    "language": a.get("language", language),
                    "published_at": a.get("seendate"),
                }
                for a in articles
            ]

    @staticmethod
    def _generate_id(url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()


class NewsApiProvider(NewsProvider):
    """Provedor NewsAPI (requer chave)."""

    provider_name = "newsapi"

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
    async def search(
        self,
        query: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        language: str = "pt",
        max_results: int = 50,
    ) -> list[dict]:
        if not settings.news_api_key:
            logger.info("NewsAPI not configured, skipping")
            return []

        params = {
            "q": query,
            "language": language,
            "pageSize": str(min(max_results, 100)),
            "sortBy": "publishedAt",
        }
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params=params,
                headers={"X-Api-Key": settings.news_api_key},
            )
            if response.status_code != 200:
                logger.warning("NewsAPI returned %d", response.status_code)
                return []

            data = response.json()
            articles = data.get("articles", [])

            return [
                {
                    "provider": "newsapi",
                    "external_id": hashlib.md5(a.get("url", "").encode()).hexdigest(),
                    "title": a.get("title", ""),
                    "description": a.get("description"),
                    "url": a.get("url", ""),
                    "image_url": a.get("urlToImage"),
                    "author": a.get("author"),
                    "source_domain": a.get("source", {}).get("name"),
                    "language": language,
                    "published_at": a.get("publishedAt"),
                }
                for a in articles
            ]


# Provider registry
PROVIDERS: dict[str, type[NewsProvider]] = {
    "gdelt": GdeltProvider,
    "newsapi": NewsApiProvider,
}


def get_active_providers() -> list[NewsProvider]:
    """Retorna instâncias dos provedores ativos."""
    active = []
    if settings.gdelt_api_url:
        active.append(GdeltProvider())
    if settings.news_api_key:
        active.append(NewsApiProvider())
    return active
