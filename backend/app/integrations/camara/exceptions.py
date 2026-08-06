"""Exceções da integração com a Câmara dos Deputados."""


class CamaraIntegrationError(Exception):
    """Erro base da integração Câmara."""
    pass


class CamaraApiError(CamaraIntegrationError):
    """Erro na comunicação com a API da Câmara."""
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(f"Câmara API error {status_code}: {message}")


class CamaraRateLimitError(CamaraIntegrationError):
    """Rate limit excedido."""
    pass


class CamaraTimeoutError(CamaraIntegrationError):
    """Timeout na requisição."""
    pass
