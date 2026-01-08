"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # Database
    database_url: str

    # Redis
    redis_url: str

    # OpenAI
    openai_api_key: str

    # Encryption
    encryption_key: str  # 32-byte hex string for AES-256-GCM

    # Slack OAuth
    slack_client_id: str
    slack_client_secret: str
    slack_redirect_uri: str

    # Telegram (via Telethon)
    telegram_api_id: str
    telegram_api_hash: str

    # Outlook OAuth
    outlook_client_id: str
    outlook_client_secret: str
    outlook_redirect_uri: str
    outlook_tenant_id: str = "common"

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Ranking configuration (hybrid semantic+recency)
    ranking_alpha: float = 0.85  # Semantic weight (0.0-1.0), default 0.85
    ranking_tau_days: float = 14.0  # Recency decay half-life in days, default 14
    rerank_candidates_topn: int = 50  # Stage A candidates before reranking, default 50
    ranking_mode: str = "weighted"  # "weighted" or "multiplier", default "weighted"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
