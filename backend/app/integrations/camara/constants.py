"""Constantes para integração com a Câmara dos Deputados."""

CAMARA_API_BASE = "https://dadosabertos.camara.leg.br/api/v2"

# Rate limit: ~50 req/min (conservative)
CAMARA_RATE_LIMIT_PER_MINUTE = 40
CAMARA_DEFAULT_PAGE_SIZE = 100
CAMARA_MAX_PAGE_SIZE = 200
CAMARA_TIMEOUT_SECONDS = 30

# Endpoints
ENDPOINTS = {
    "deputies": "/deputados",
    "deputy_detail": "/deputados/{id}",
    "deputy_expenses": "/deputados/{id}/despesas",
    "deputy_speeches": "/deputados/{id}/discursos",
    "deputy_fronts": "/deputados/{id}/frentes",
    "deputy_committees": "/deputados/{id}/orgaos",
    "deputy_events": "/deputados/{id}/eventos",
    "propositions": "/proposicoes",
    "proposition_detail": "/proposicoes/{id}",
    "proposition_authors": "/proposicoes/{id}/autores",
    "proposition_events": "/proposicoes/{id}/tramitacoes",
    "votes": "/votacoes",
    "vote_detail": "/votacoes/{id}",
    "vote_voters": "/votacoes/{id}/votos",
    "committees": "/orgaos",
    "committee_members": "/orgaos/{id}/membros",
    "fronts": "/frentes",
    "legislatures": "/legislaturas",
}

# Vote normalization
VOTE_MAP = {
    "Sim": "yes",
    "Não": "no",
    "Abstenção": "abstention",
    "Obstrução": "obstruction",
    "Art. 17": "art17",
    "Presidente": "president",
    "-": "absent",
}

# Expense categories (CEAP)
EXPENSE_CATEGORIES = [
    "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
    "COMBUSTÍVEIS E LUBRIFICANTES",
    "CONSULTORIAS, PESQUISAS E TRABALHOS TÉCNICOS",
    "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR",
    "PASSAGENS AÉREAS",
    "TELEFONIA",
    "SERVIÇOS POSTAIS",
    "HOSPEDAGEM",
    "ALIMENTAÇÃO DO PARLAMENTAR",
    "LOCAÇÃO OU FRETAMENTO DE VEÍCULOS AUTOMOTORES",
    "SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO",
    "PARTICIPAÇÃO EM CURSO, PALESTRA OU EVENTO SIMILAR",
    "ASSINATURA DE PUBLICAÇÕES",
    "LOCAÇÃO OU FRETAMENTO DE EMBARCAÇÕES",
    "LOCAÇÃO OU FRETAMENTO DE AERONAVES",
    "SERVIÇO DE SEGURANÇA",
    "EMISSÃO BILHETE AÉREO",
]
