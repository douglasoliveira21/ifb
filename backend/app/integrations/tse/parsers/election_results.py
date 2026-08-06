"""Parser de resultados eleitorais do TSE."""

import logging

from app.integrations.tse.parsers.base import TseDatasetParser
from app.integrations.tse.schemas import TseResultRow

logger = logging.getLogger(__name__)


class TseElectionResultsParser(TseDatasetParser):
    """Parser para resultados eleitorais."""

    dataset_type = "election_results"
    required_columns = {"SQ_CANDIDATO", "QT_VOTOS_NOMINAIS"}

    def parse_row(self, row: dict[str, str], year: int) -> TseResultRow | None:
        votes_str = row.get("QT_VOTOS_NOMINAIS", "0")
        try:
            votes = int(votes_str) if votes_str and votes_str != "#NULO#" else 0
        except ValueError:
            votes = 0

        sequence = row.get("SQ_CANDIDATO", "").strip()
        if not sequence or sequence == "#NULO#":
            return None

        result_status = row.get("DS_SIT_TOT_TURNO", "").strip()
        elected = result_status.upper() in (
            "ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA"
        )

        round_str = row.get("NR_TURNO", "1")
        try:
            round_num = int(round_str) if round_str else 1
        except ValueError:
            round_num = 1

        return TseResultRow(
            election_year=year,
            state_code=row.get("SG_UF", ""),
            city_code=row.get("CD_MUNICIPIO"),
            sequence_number=sequence,
            ballot_number=row.get("NR_CANDIDATO"),
            candidate_name=row.get("NM_CANDIDATO"),
            round=round_num,
            votes=votes,
            result_status=result_status,
            elected=elected,
        )
