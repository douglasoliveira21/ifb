"""Exceções específicas da integração TSE."""


class TseIntegrationError(Exception):
    """Erro base da integração TSE."""
    pass


class TseDownloadError(TseIntegrationError):
    """Erro ao baixar dataset do TSE."""
    pass


class TseParseError(TseIntegrationError):
    """Erro ao parsear arquivo do TSE."""
    pass


class TseLayoutError(TseIntegrationError):
    """Layout inesperado (colunas faltando ou diferentes)."""
    pass


class TseReconciliationError(TseIntegrationError):
    """Erro durante conciliação de candidato com político."""
    pass


class TseChecksumMismatch(TseIntegrationError):
    """Checksum do arquivo não confere."""
    pass
