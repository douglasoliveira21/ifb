"""Provedores e normalizadores de notícias."""

import hashlib
import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

TRACKING_QUERY_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "referrer",
}


def normalize_url(url: str | None) -> str:
    """Normaliza URLs HTTP(S), removendo fragmentos e parâmetros de rastreamento."""
    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
            return ""

        scheme = parts.scheme.lower()
        host = parts.hostname.lower().rstrip(".")
        port = parts.port
        netloc = host
        if port and (scheme, port) not in {("http", 80), ("https", 443)}:
            netloc = f"{host}:{port}"

        query_items = [
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if not key.lower().startswith("utm_")
            and key.lower() not in TRACKING_QUERY_PARAMETERS
        ]
        return urlunsplit((scheme, netloc, parts.path or "/", urlencode(query_items), ""))
    except ValueError:
        return ""


def extract_domain(url: str | None) -> str | None:
    """Extrai um domínio normalizado de URL HTTP(S)."""
    normalized = normalize_url(url)
    if not normalized:
        return None
    hostname = urlsplit(normalized).hostname
    return hostname.lower() if hostname else None


def parse_published_at(value: datetime | str | None) -> datetime | None:
    """Converte datas dos provedores para ``datetime`` com fuso UTC."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not value:
        return None

    raw = value.strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(raw.rstrip("Zz"), "%Y%m%dT%H%M%S")
        except ValueError:
            try:
                parsed = parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


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
        """Busca notícias e retorna itens normalizados."""


class GoogleNewsRssProvider(NewsProvider):
    """Coleta resultados do feed RSS do Google News, sem publicar conteúdo."""

    provider_name = "google_news_rss"
    feed_url = "https://news.google.com/rss/search"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=15))
    async def search(
        self,
        query: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        language: str = "pt",
        max_results: int = 50,
    ) -> list[dict]:
        del start_date, end_date, language
        params = {
            "q": query,
            "hl": "pt-BR",
            "gl": "BR",
            "ceid": "BR:pt-419",
        }

        async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
            response = await client.get(self.feed_url, params=params)
            if response.status_code != 200:
                logger.warning("Google News RSS returned %d", response.status_code)
                return []

            try:
                root = ET.fromstring(response.content)
            except ET.ParseError:
                logger.warning("Google News RSS returned invalid XML")
                return []

            articles: list[dict] = []
            for item in root.findall(".//item")[: min(max_results, 100)]:
                original_url = normalize_url(item.findtext("link"))
                if not original_url:
                    continue

                source_element = item.find("source")
                source_name = source_element.text.strip() if source_element is not None and source_element.text else None
                source_url = source_element.get("url") if source_element is not None else None
                canonical_url = await self._resolve_canonical_url(client, original_url)
                source_domain = extract_domain(canonical_url) or extract_domain(source_url)

                articles.append(
                    {
                        "provider": self.provider_name,
                        "external_id": hashlib.sha256(
                            (canonical_url or original_url).encode("utf-8")
                        ).hexdigest(),
                        "title": item.findtext("title", "").strip(),
                        "url": canonical_url or original_url,
                        "original_url": original_url,
                        "source_domain": source_domain,
                        "source_name": source_name,
                        "language": "pt",
                        "published_at": parse_published_at(item.findtext("pubDate")),
                    }
                )
            return articles

    async def _resolve_canonical_url(self, client: httpx.AsyncClient, url: str) -> str:
        """Segue apenas links do agregador e mantém a URL original quando não houver redirecionamento."""
        domain = extract_domain(url)
        if domain != "news.google.com":
            return url

        try:
            async with client.stream("GET", url, follow_redirects=True) as response:
                if response.status_code < 400:
                    return normalize_url(str(response.url)) or url
                logger.warning("Google News redirect returned %d", response.status_code)
        except httpx.HTTPError as exc:
            logger.info("Unable to resolve Google News redirect: %s", exc)
        return url


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
                settings.gdelt_api_url.rstrip("/") + "/doc/doc",
                params=params,
            )
            if response.status_code != 200:
                logger.warning("GDELT returned %d", response.status_code)
                return []

            articles = response.json().get("articles", [])
            return [
                {
                    "provider": self.provider_name,
                    "external_id": self._generate_id(a.get("url", "")),
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "image_url": a.get("socialimage"),
                    "source_domain": extract_domain(a.get("url")) or a.get("domain"),
                    "source_name": a.get("domain"),
                    "language": a.get("language", language),
                    "published_at": parse_published_at(a.get("seendate")),
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

            articles = response.json().get("articles", [])
            return [
                {
                    "provider": self.provider_name,
                    "external_id": hashlib.md5(a.get("url", "").encode()).hexdigest(),
                    "title": a.get("title", ""),
                    "description": a.get("description"),
                    "url": a.get("url", ""),
                    "image_url": a.get("urlToImage"),
                    "author": a.get("author"),
                    "source_domain": extract_domain(a.get("url")),
                    "source_name": a.get("source", {}).get("name"),
                    "language": language,
                    "published_at": parse_published_at(a.get("publishedAt")),
                }
                for a in articles
            ]


PROVIDERS: dict[str, type[NewsProvider]] = {
    "google_news_rss": GoogleNewsRssProvider,
    "gdelt": GdeltProvider,
    "newsapi": NewsApiProvider,
}


def get_active_providers() -> list[NewsProvider]:
    """Retorna provedores configurados, priorizando o RSS do Google News."""
    active: list[NewsProvider] = []
    if settings.google_news_rss_enabled:
        active.append(GoogleNewsRssProvider())
    if settings.gdelt_api_url:
        active.append(GdeltProvider())
    if settings.news_api_key:
        active.append(NewsApiProvider())
    return active
