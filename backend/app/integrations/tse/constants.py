"""Constantes para a integração com TSE."""

# Portal de Dados Abertos do TSE
TSE_DATA_URL = "https://dadosabertos.tse.jus.br"
TSE_CANDIDATES_BASE = "https://dadosabertos.tse.jus.br/dataset/candidatos"

# DivulgaCandContas (referência complementar)
DIVULGA_CAND_URL = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"

# Supported election years
SUPPORTED_YEARS = [2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026]

# Election types
ELECTION_TYPES = {
    "general": "Eleições Gerais",
    "municipal": "Eleições Municipais",
    "supplementary": "Eleição Suplementar",
}

# Candidacy status mapping (TSE → IFB)
CANDIDACY_STATUS_MAP = {
    "APTO": "deferido",
    "DEFERIDO": "deferido",
    "DEFERIDO COM RECURSO": "deferido_com_recurso",
    "INDEFERIDO": "indeferido",
    "INDEFERIDO COM RECURSO": "indeferido_com_recurso",
    "CANCELADO": "cancelado",
    "CASSADO": "cassado",
    "RENÚNCIA": "renuncia",
    "FALECIDO": "falecido",
    "NÃO CONHECIDO": "nao_conhecido",
    "PENDENTE DE JULGAMENTO": "pendente",
}

# Election result status mapping
RESULT_STATUS_MAP = {
    "ELEITO": "eleito",
    "ELEITO POR QP": "eleito",
    "ELEITO POR MÉDIA": "eleito_media",
    "NÃO ELEITO": "nao_eleito",
    "SUPLENTE": "suplente",
    "2º TURNO": "segundo_turno",
    "#NULO#": "nulo",
    "#NE#": "nao_eleito",
    "MÉDIA": "eleito_media",
}

# CSV encoding common in TSE files
TSE_CSV_ENCODING = "latin-1"
TSE_CSV_SEPARATOR = ";"

# Brazilian states
UF_CODES = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "BR",
]
