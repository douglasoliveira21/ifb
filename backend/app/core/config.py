"""Configurações centralizadas da aplicação."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações do sistema carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    app_name: str = "Instituto Fiscaliza Brasil"
    app_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ifb"
    postgres_user: str = "ifb"
    postgres_password: str = "ifb_secret"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_access_expires_minutes: int = 15
    jwt_refresh_expires_days: int = 7
    jwt_algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # AI (DeepSeek / OpenAI-compatible)
    openai_api_key: str = ""
    openai_api_base_url: str = "https://api.deepseek.com"
    openai_model: str = "deepseek-v4-flash"

    # External APIs
    tse_api_url: str = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"
    camara_api_url: str = "https://dadosabertos.camara.leg.br/api/v2"
    senado_api_url: str = "https://legis.senado.leg.br/dadosabertos"
    transparencia_api_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"
    transparencia_api_key: str = ""

    # News
    news_api_key: str = ""
    gdelt_api_url: str = "https://api.gdeltproject.org/api/v2"
    bing_news_api_key: str = ""

    # S3/MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "ifb"

    # SMTP
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@fiscalizabrasil.org.br"

    # Sentry
    sentry_dsn: str = ""

    # HIBP (Have I Been Pwned) password check
    hibp_enabled: bool = False
    hibp_timeout_seconds: int = 3
    hibp_reject_compromised: bool = True

    # Payment
    payment_provider: str = ""
    payment_api_key: str = ""
    payment_webhook_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
