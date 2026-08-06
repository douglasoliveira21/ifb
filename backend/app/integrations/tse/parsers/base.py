"""Base class para parsers de datasets do TSE."""

import csv
import hashlib
import logging
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path

from app.integrations.tse.constants import TSE_CSV_ENCODING, TSE_CSV_SEPARATOR
from app.integrations.tse.exceptions import TseLayoutError, TseParseError

logger = logging.getLogger(__name__)


class TseDatasetParser(ABC):
    """Interface base para parsers de datasets TSE."""

    dataset_type: str = ""
    supported_years: set[int] = set()
    required_columns: set[str] = set()

    def detect_encoding(self, file_path: str) -> str:
        """Detecta encoding tentando ler primeiras linhas."""
        for enc in ("latin-1", "utf-8", "cp1252"):
            try:
                with open(file_path, "r", encoding=enc) as f:
                    f.readline()
                return enc
            except (UnicodeDecodeError, UnicodeError):
                continue
        return TSE_CSV_ENCODING

    def detect_separator(self, file_path: str, encoding: str) -> str:
        """Detecta separador (`;` ou `,`)."""
        with open(file_path, "r", encoding=encoding) as f:
            first_line = f.readline()
        if first_line.count(";") > first_line.count(","):
            return ";"
        return ","

    def get_layout_hash(self, headers: list[str]) -> str:
        """Gera hash dos cabeçalhos para identificar layout."""
        normalized = "|".join(sorted(h.strip().upper() for h in headers))
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def validate_headers(self, headers: list[str]) -> None:
        """Valida que colunas obrigatórias estão presentes."""
        header_set = {h.strip().upper() for h in headers}
        missing = self.required_columns - header_set
        if missing:
            raise TseLayoutError(
                f"[{self.dataset_type}] Missing columns: {missing}"
            )

    @abstractmethod
    def parse_row(self, row: dict[str, str], year: int) -> object | None:
        """Parseia uma linha do CSV. Retorna None para pular."""
        ...

    def parse_file(
        self,
        file_path: str,
        year: int,
        encoding: str | None = None,
        separator: str | None = None,
    ) -> Generator[object, None, None]:
        """
        Lê arquivo CSV em streaming.
        Aceita arquivos .csv e .zip contendo CSVs.
        """
        path = Path(file_path)
        if not path.exists():
            raise TseParseError(f"File not found: {file_path}")

        # Handle ZIP files
        if path.suffix.lower() == ".zip":
            yield from self._parse_zip(path, year, encoding, separator)
            return

        enc = encoding or self.detect_encoding(file_path)
        sep = separator or self.detect_separator(file_path, enc)

        yield from self._parse_csv(file_path, year, enc, sep)

    def _parse_csv(
        self, file_path: str, year: int, encoding: str, separator: str
    ) -> Generator[object, None, None]:
        """Parse um arquivo CSV."""
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=separator, quotechar='"')
            if not reader.fieldnames:
                raise TseLayoutError(f"Empty CSV: {file_path}")

            self.validate_headers(list(reader.fieldnames))
            layout_hash = self.get_layout_hash(list(reader.fieldnames))
            logger.info(
                "[%s] Parsing %s (layout=%s, year=%d)",
                self.dataset_type, file_path, layout_hash, year,
            )

            row_count = 0
            error_count = 0
            for row in reader:
                row_count += 1
                try:
                    result = self.parse_row(row, year)
                    if result:
                        yield result
                except Exception as e:
                    error_count += 1
                    if error_count <= 10:
                        logger.warning(
                            "[%s] Row %d error: %s", self.dataset_type, row_count, e
                        )

            logger.info(
                "[%s] Done: %d rows, %d errors",
                self.dataset_type, row_count, error_count,
            )

    def _parse_zip(
        self, zip_path: Path, year: int, encoding: str | None, separator: str | None
    ) -> Generator[object, None, None]:
        """Extrai e parseia CSVs de dentro de um ZIP."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_files = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_files:
                raise TseParseError(f"No CSV files in ZIP: {zip_path}")

            for csv_name in csv_files:
                logger.info("[%s] Extracting %s from ZIP", self.dataset_type, csv_name)
                # Extract to temp location alongside zip
                extracted = zip_path.parent / csv_name
                with zf.open(csv_name) as src, open(extracted, "wb") as dst:
                    while chunk := src.read(65536):
                        dst.write(chunk)

                try:
                    enc = encoding or self.detect_encoding(str(extracted))
                    sep = separator or self.detect_separator(str(extracted), enc)
                    yield from self._parse_csv(str(extracted), year, enc, sep)
                finally:
                    extracted.unlink(missing_ok=True)
