"""Mapeadores TSE → modelos internos IFB."""

import hashlib
from datetime import UTC, datetime

from app.integrations.tse.constants import CANDIDACY_STATUS_MAP, RESULT_STATUS_MAP
from app.integrations.tse.schemas import TseAssetRow, TseCandidateRow, TseResultRow


def hash_cpf(cpf: str) -> str:
    """Gera hash SHA-256 do CPF para deduplicação segura."""
    normalized = cpf.strip().replace(".", "").replace("-", "")
    return hashlib.sha256(normalized.encode()).hexdigest()


def hash_document(doc: str) -> str:
    """Gera hash de documento (CPF/CNPJ) para armazenamento."""
    cleaned = doc.strip().replace(".", "").replace("-", "").replace("/", "")
    return hashlib.sha256(cleaned.encode()).hexdigest()


def map_candidacy_status(tse_status: str | None) -> str:
    """Mapeia status TSE para status interno."""
    if not tse_status:
        return "unknown"
    normalized = tse_status.strip().upper()
    return CANDIDACY_STATUS_MAP.get(normalized, "unknown")


def map_result_status(tse_status: str | None) -> tuple[str, bool]:
    """
    Mapeia resultado TSE para (status, elected).
    """
    if not tse_status:
        return "unknown", False
    normalized = tse_status.strip().upper()
    mapped = RESULT_STATUS_MAP.get(normalized, "unknown")
    elected = mapped in ("eleito", "eleito_media")
    return mapped, elected


def parse_tse_date(date_str: str | None) -> datetime | None:
    """Parseia data TSE (formatos: dd/mm/yyyy ou yyyy-mm-dd)."""
    if not date_str or date_str.strip() in ("", "#NULO#", "#NE#"):
        return None
    date_str = date_str.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def parse_tse_value(value_str: str | None) -> float:
    """Parseia valor monetário TSE (vírgula como decimal)."""
    if not value_str or value_str.strip() in ("", "#NULO#", "#NE#"):
        return 0.0
    cleaned = value_str.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def candidate_to_dict(row: TseCandidateRow) -> dict:
    """Converte TseCandidateRow para dict preparado para o banco."""
    cpf_h = hash_cpf(row.cpf) if row.cpf else None
    birth = parse_tse_date(row.birth_date)

    return {
        "full_name": row.full_name,
        "ballot_name": row.ballot_name,
        "cpf_hash": cpf_h,
        "birth_date": birth,
        "gender": row.gender,
        "race_color": row.race_color,
        "marital_status": row.marital_status,
        "education": row.education,
        "occupation": row.occupation,
        "nationality": row.nationality,
        "birth_place": f"{row.birth_city}/{row.birth_state}" if row.birth_city else row.birth_state,
        "state_code": row.state_code,
        "city_name": row.city_name,
        "sequence_number": row.sequence_number,
        "ballot_number": row.ballot_number,
        "party_acronym": row.party_acronym,
        "position_name": row.position_name,
        "coalition_name": row.coalition_name,
        "coalition_parties": row.coalition_parties,
        "status": map_candidacy_status(row.candidacy_status),
        "status_detail": row.candidacy_status_detail,
        "reelection": row.reelection,
        "collected_at": datetime.now(UTC),
    }
