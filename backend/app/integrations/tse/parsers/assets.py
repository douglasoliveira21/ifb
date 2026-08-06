"""Parser de bens declarados do TSE."""

import logging

from app.integrations.tse.mappers import parse_tse_value
from app.integrations.tse.parsers.base import TseDatasetParser
from app.integrations.tse.schemas import TseAssetRow

logger = logging.getLogger(__name__)


class TseAssetsParser(TseDatasetParser):
    """Parser para bens declarados à Justiça Eleitoral."""

    dataset_type = "assets"
    required_columns = {"SQ_CANDIDATO", "DS_BEM_CANDIDATO", "VR_BEM_CANDIDATO"}

    def parse_row(self, row: dict[str, str], year: int) -> TseAssetRow | None:
        description = row.get("DS_BEM_CANDIDATO", "").strip()
        if not description or description == "#NULO#":
            return None

        value = parse_tse_value(row.get("VR_BEM_CANDIDATO"))

        return TseAssetRow(
            election_year=year,
            sequence_number=row.get("SQ_CANDIDATO"),
            candidate_sequence=row.get("SQ_CANDIDATO"),
            category_code=row.get("CD_TIPO_BEM_CANDIDATO"),
            category_name=row.get("DS_TIPO_BEM_CANDIDATO"),
            description=description,
            declared_value=value,
        )
