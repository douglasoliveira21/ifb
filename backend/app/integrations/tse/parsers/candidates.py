"""Parser de candidatos do TSE (CSV)."""

import csv
import logging
from collections.abc import Generator
from pathlib import Path

from app.integrations.tse.constants import TSE_CSV_ENCODING, TSE_CSV_SEPARATOR
from app.integrations.tse.exceptions import TseLayoutError, TseParseError
from app.integrations.tse.schemas import TseCandidateRow

logger = logging.getLogger(__name__)

# Required columns (minimum set across multiple years)
REQUIRED_COLUMNS = {"NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_UF"}

# Column mappings for different years (normalized)
COLUMN_MAP = {
    "ANO_ELEICAO": "election_year",
    "CD_TIPO_ELEICAO": "election_type",
    "SG_UF": "state_code",
    "CD_MUNICIPIO": "city_code",
    "NM_MUNICIPIO": "city_name",
    "SQ_CANDIDATO": "sequence_number",
    "NR_CANDIDATO": "ballot_number",
    "NM_CANDIDATO": "full_name",
    "NM_URNA_CANDIDATO": "ballot_name",
    "NR_CPF_CANDIDATO": "cpf",
    "DT_NASCIMENTO": "birth_date",
    "CD_GENERO": "gender",
    "CD_COR_RACA": "race_color",
    "CD_ESTADO_CIVIL": "marital_status",
    "CD_GRAU_INSTRUCAO": "education",
    "CD_OCUPACAO": "occupation",
    "SG_PARTIDO": "party_acronym",
    "NR_PARTIDO": "party_number",
    "NM_COLIGACAO": "coalition_name",
    "DS_COMPOSICAO_COLIGACAO": "coalition_parties",
    "CD_CARGO": "position_code",
    "DS_CARGO": "position_name",
    "DS_SIT_TOT_TURNO": "candidacy_status",
    "DS_DETALHE_SITUACAO_CAND": "candidacy_status_detail",
    "ST_REELEICAO": "reelection",
    "NM_EMAIL": "email",
    "SG_UF_NASCIMENTO": "birth_state",
    "NM_MUNICIPIO_NASCIMENTO": "birth_city",
    "DS_NACIONALIDADE": "nationality",
}


def parse_candidates_csv(
    file_path: str,
    year: int,
    encoding: str = TSE_CSV_ENCODING,
    separator: str = TSE_CSV_SEPARATOR,
) -> Generator[TseCandidateRow, None, None]:
    """
    Lê CSV de candidatos do TSE e gera registros normalizados.
    Usa streaming - não carrega o arquivo inteiro na memória.
    """
    path = Path(file_path)
    if not path.exists():
        raise TseParseError(f"File not found: {file_path}")

    try:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            # Detect header
            reader = csv.DictReader(f, delimiter=separator, quotechar='"')
            if not reader.fieldnames:
                raise TseLayoutError("Empty CSV or no header")

            # Validate required columns exist
            header_set = set(reader.fieldnames)
            missing = REQUIRED_COLUMNS - header_set
            if missing:
                raise TseLayoutError(
                    f"Missing required columns for year {year}: {missing}"
                )

            row_count = 0
            for row in reader:
                row_count += 1
                try:
                    candidate = _map_row(row, year)
                    if candidate:
                        yield candidate
                except Exception as e:
                    logger.warning("Row %d parse error: %s", row_count, str(e))
                    continue

            logger.info("Parsed %d rows from %s", row_count, file_path)

    except UnicodeDecodeError:
        raise TseParseError(f"Encoding error in {file_path}. Try different encoding.")


def _map_row(row: dict, year: int) -> TseCandidateRow | None:
    """Mapeia uma linha do CSV para TseCandidateRow."""
    full_name = row.get("NM_CANDIDATO", "").strip()
    ballot_name = row.get("NM_URNA_CANDIDATO", "").strip()

    if not full_name or full_name == "#NULO#":
        return None

    reelection_raw = row.get("ST_REELEICAO", "N")
    reelection = reelection_raw.upper() in ("S", "SIM", "1", "TRUE")

    return TseCandidateRow(
        election_year=year,
        election_type=row.get("CD_TIPO_ELEICAO", ""),
        state_code=row.get("SG_UF", ""),
        city_code=row.get("CD_MUNICIPIO"),
        city_name=row.get("NM_MUNICIPIO"),
        sequence_number=row.get("SQ_CANDIDATO"),
        ballot_number=row.get("NR_CANDIDATO"),
        full_name=full_name,
        ballot_name=ballot_name or full_name,
        cpf=_clean_cpf(row.get("NR_CPF_CANDIDATO", "")),
        birth_date=row.get("DT_NASCIMENTO"),
        gender=row.get("CD_GENERO"),
        race_color=row.get("CD_COR_RACA"),
        marital_status=row.get("CD_ESTADO_CIVIL"),
        education=row.get("CD_GRAU_INSTRUCAO"),
        occupation=row.get("CD_OCUPACAO"),
        nationality=row.get("DS_NACIONALIDADE"),
        birth_state=row.get("SG_UF_NASCIMENTO"),
        birth_city=row.get("NM_MUNICIPIO_NASCIMENTO"),
        party_acronym=row.get("SG_PARTIDO"),
        party_number=row.get("NR_PARTIDO"),
        coalition_name=row.get("NM_COLIGACAO"),
        coalition_parties=row.get("DS_COMPOSICAO_COLIGACAO"),
        position_code=row.get("CD_CARGO"),
        position_name=row.get("DS_CARGO"),
        candidacy_status=row.get("DS_SIT_TOT_TURNO"),
        candidacy_status_detail=row.get("DS_DETALHE_SITUACAO_CAND"),
        reelection=reelection,
    )


def _clean_cpf(cpf: str) -> str | None:
    """Limpa CPF removendo formatação. Retorna None se inválido."""
    if not cpf:
        return None
    cleaned = cpf.replace(".", "").replace("-", "").replace(" ", "").strip()
    if len(cleaned) != 11 or cleaned == "00000000000":
        return None
    return cleaned
