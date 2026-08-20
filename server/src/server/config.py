"""PullSense Server — Configuration via Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable validation.

    All settings are loaded from environment variables or a `.env` file.
    The application fails fast at startup if required settings are missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    app_env: str = "development"
    app_debug: bool = False
    app_log_level: str = "INFO"
    app_cors_origins: list[str] = ["http://localhost:3000"]
    app_title: str = "PullSense API"
    app_version: str = "0.1.0"

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pullsense"

    # Connection pool
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # ── Redis ────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Celery ───────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── Clerk Authentication ─────────────────────────────────────────────
    clerk_secret_key: str = ""
    clerk_webhook_secret: str = ""
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""

    # ── GitHub App ───────────────────────────────────────────────────────
    github_app_id: int = 0
    github_app_private_key: str = ""
    github_webhook_secret: str = ""
    github_app_client_id: str = ""
    github_app_client_secret: str = ""

    # ── GCP Vertex AI & Agent Platform (ADK) ────────────────────────────
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    google_application_credentials: str | None = None
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    embedding_model: str = "text-embedding-004"

    # ── Pinecone ─────────────────────────────────────────────────────────
    pinecone_api_key: str = ""
    pinecone_index_name: str = "pullsense"

    # ── Rate Limiting ────────────────────────────────────────────────────
    rate_limit_reviews_per_hour: int = 100

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance. Call this instead of constructing directly."""
    return Settings()
