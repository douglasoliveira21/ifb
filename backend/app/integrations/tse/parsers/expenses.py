"""Parser de despesas de campanha do TSE."""

import logging

from app.integrations.tse.mappers import parse_tse_value
from app.integrations.tse.parsers.base import TseDatasetParser
from app.integrations.tse.schemas import TseExpenseRow

logger = logging.getLogger(__name__)


class TseExpensesParser(TseDatasetParser):
    """Parser para despesas de campanha eleitoral."""

    dataset_type = "expenses"
    required_columns = {"SQ_CANDIDATO", "VR_DESPESA_CONTRATADA"}

    def parse_row(self, row: dict[str, str], year: int) -> TseExpenseRow | None:
        amount = parse_tse_value(
            row.get("VR_DESPESA_CONTRATADA") or row.get("VR_PAGTO_DESPESA")
        )
        if amount == 0.0:
            return None

        return TseExpenseRow(
            election_year=year,
            sequence_number=row.get("SQ_CANDIDATO"),
            supplier_name=row.get("NM_FORNECEDOR", "").strip() or None,
            supplier_cpf_cnpj=row.get("NR_CPF_CNPJ_FORNECEDOR", "").strip() or None,
            expense_type=row.get("DS_TIPO_DESPESA") or row.get("DS_NATUREZA_DESPESA"),
            description=row.get("DS_DESPESA"),
            amount=amount,
            contracted_at=row.get("DT_DESPESA"),
            paid_at=row.get("DT_PAGTO_DESPESA"),
            document_number=row.get("NR_DOCUMENTO_DESPESA"),
        )
