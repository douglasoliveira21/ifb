"""Schemas de dados do TSE (estrutura dos CSVs)."""

from pydantic import BaseModel


class TseCandidateRow(BaseModel):
    """Representação normalizada de uma linha de candidato do TSE."""

    election_year: int
    election_type: str
    state_code: str
    city_code: str | None = None
    city_name: str | None = None
    sequence_number: str | None = None
    ballot_number: str | None = None
    full_name: str
    ballot_name: str
    cpf: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    race_color: str | None = None
    marital_status: str | None = None
    education: str | None = None
    occupation: str | None = None
    nationality: str | None = None
    birth_state: str | None = None
    birth_city: str | None = None
    party_acronym: str | None = None
    party_number: str | None = None
    coalition_name: str | None = None
    coalition_parties: str | None = None
    position_code: str | None = None
    position_name: str | None = None
    candidacy_status: str | None = None
    candidacy_status_detail: str | None = None
    reelection: bool = False
    email: str | None = None  # Not stored - used only for verification


class TseAssetRow(BaseModel):
    """Representação normalizada de um bem declarado."""

    election_year: int
    sequence_number: str | None = None
    candidate_sequence: str | None = None
    category_code: str | None = None
    category_name: str | None = None
    description: str
    declared_value: float


class TseRevenueRow(BaseModel):
    """Representação normalizada de uma receita de campanha."""

    election_year: int
    sequence_number: str | None = None
    receipt_number: str | None = None
    donor_name: str | None = None
    donor_cpf_cnpj: str | None = None
    donor_type: str | None = None
    revenue_type: str | None = None
    resource_source: str | None = None
    amount: float
    received_at: str | None = None
    description: str | None = None


class TseExpenseRow(BaseModel):
    """Representação normalizada de uma despesa de campanha."""

    election_year: int
    sequence_number: str | None = None
    supplier_name: str | None = None
    supplier_cpf_cnpj: str | None = None
    expense_type: str | None = None
    description: str | None = None
    amount: float
    contracted_at: str | None = None
    paid_at: str | None = None
    document_number: str | None = None


class TseResultRow(BaseModel):
    """Representação normalizada de resultado eleitoral."""

    election_year: int
    state_code: str
    city_code: str | None = None
    sequence_number: str | None = None
    ballot_number: str | None = None
    candidate_name: str | None = None
    round: int = 1
    votes: int = 0
    result_status: str | None = None
    elected: bool = False
