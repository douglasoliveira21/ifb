"""Exceções da integração com o Senado Federal."""


class SenadoIntegrationError(Exception):
    """Erro base da integração Senado."""
    pass


class SenadoApiError(SenadoIntegrationError):
    """Erro na comunicação com a API do Senado."""
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(f"Senado API error {status_code}: {message}")


class SenadoRateLimitError(SenadoIntegrationError):
    """Rate limit excedido."""
    pass
