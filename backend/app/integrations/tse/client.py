"""Cliente HTTP para o Portal de Dados Abertos do TSE."""

import hashlib
import logging
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.integrations.tse.constants import TSE_DATA_URL
from app.integrations.tse.exceptions import TseDownloadError

settings = get_settings()
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


class TseClient:
    """Cliente para download de datasets do TSE."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": "IFB-Platform/1.0 (fiscalizabrasil.org.br)"},
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=5, max=60))
    async def download_file(
        self,
        url: str,
        dest_path: str,
        expected_checksum: str | None = None,
    ) -> dict:
        """
        Faz download de arquivo via streaming.
        Retorna metadata: {path, size, checksum, content_type}.
        """
        client = await self._get_client()
        logger.info("Downloading TSE file: %s", url)

        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > MAX_FILE_SIZE:
                    raise TseDownloadError(
                        f"File too large: {content_length} bytes (max {MAX_FILE_SIZE})"
                    )

                hasher = hashlib.sha256()
                total_size = 0

                dest = Path(dest_path)
                dest.parent.mkdir(parents=True, exist_ok=True)

                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
                        hasher.update(chunk)
                        total_size += len(chunk)

                        if total_size > MAX_FILE_SIZE:
                            dest.unlink(missing_ok=True)
                            raise TseDownloadError("File exceeded max size during download")

                checksum = hasher.hexdigest()

                if expected_checksum and checksum != expected_checksum:
                    logger.warning(
                        "Checksum mismatch: expected %s, got %s",
                        expected_checksum, checksum,
                    )

                content_type = response.headers.get("content-type", "")

                logger.info("Downloaded %s (%d bytes, sha256=%s)", url, total_size, checksum[:12])
                return {
                    "path": str(dest),
                    "size": total_size,
                    "checksum": checksum,
                    "content_type": content_type,
                }

        except httpx.HTTPStatusError as e:
            raise TseDownloadError(f"HTTP {e.response.status_code}: {url}") from e
        except httpx.TimeoutException as e:
            raise TseDownloadError(f"Timeout downloading: {url}") from e

    async def head(self, url: str) -> dict:
        """Faz HEAD request para verificar metadata sem baixar."""
        client = await self._get_client()
        response = await client.head(url)
        return {
            "status": response.status_code,
            "content_length": response.headers.get("content-length"),
            "last_modified": response.headers.get("last-modified"),
            "etag": response.headers.get("etag"),
        }
