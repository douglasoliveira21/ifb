"""Constantes para integração com o Senado Federal."""

SENADO_API_BASE = "https://legis.senado.leg.br/dadosabertos"

SENADO_RATE_LIMIT_PER_MINUTE = 30
SENADO_DEFAULT_PAGE_SIZE = 100
SENADO_TIMEOUT_SECONDS = 30

ENDPOINTS = {
    "senators": "/senador/lista/atual",
    "senator_detail": "/senador/{code}",
    "senator_mandates": "/senador/{code}/mandatos",
    "senator_committees": "/senador/{code}/comissoes",
    "senator_votes": "/senador/{code}/votacoes",
    "matters": "/materia/pesquisa/lista",
    "matter_detail": "/materia/{id}",
    "matter_events": "/materia/{id}/movimentacoes",
    "votes": "/plenario/lista/votacao/{year}{month}",
    "vote_detail": "/plenario/votacao/{code}",
    "sessions": "/plenario/lista/sessoes/{year}{month}",
    "committees": "/comissao/lista/atual",
}

# Vote normalization for Senado
VOTE_MAP = {
    "Sim": "yes",
    "Não": "no",
    "Abstenção": "abstention",
    "NCom": "absent",
    "Obstrução": "obstruction",
    "P-NRV": "president",
    "Presidente": "president",
    "MIS": "mission",
    "AP": "excused",
    "LP": "leave",
    "LS": "medical_leave",
}
