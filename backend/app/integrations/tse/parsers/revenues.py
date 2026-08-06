"""Parser de receitas de campanha do TSE."""

import logging

from app.integrations.tse.mappers import parse_tse_value
from app.integrations.tse.parsers.base import TseDatasetParser
from app.integrations.tse.schemas import TseRevenueRow

logger = logging.getLogger(__name__)


class TseRevenuesParser(TseDatasetParser):
    """Parser para receitas de campanha eleitoral."""

    dataset_type = "revenues"
    required_columns = {"SQ_CANDIDATO", "VR_RECEITA"}

    def parse_row(self, row: dict[str, str], year: int) -> TseRevenueRow | None:
        amount = parse_tse_value(row.get("VR_RECEITA"))
        if amount == 0.0:
            return None

        return TseRevenueRow(
            election_year=year,
            sequence_number=row.get("SQ_CANDIDATO"),
            receipt_number=row.get("NR_RECIBO_ELEITORAL"),
            donor_name=row.get("NM_DOADOR", "").strip() or None,
            donor_cpf_cnpj=row.get("NR_CPF_CNPJ_DOADOR", "").strip() or None,
            donor_type=row.get("DS_TITULO_DOADOR_ORIGINARIO") or row.get("TP_DOADOR"),
            revenue_type=row.get("DS_FONTE_RECEITA") or row.get("DS_TIPO_RECEITA"),
            resource_source=row.get("DS_ORIGEM_RECEITA"),
            amount=amount,
            received_at=row.get("DT_RECEITA"),
            description=row.get("DS_RECEITA"),
        )
