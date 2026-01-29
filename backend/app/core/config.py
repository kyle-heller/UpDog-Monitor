from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/updog_dev"
    )

    # Discord webhook for alerts (optional - alerts disabled if not set)
    discord_webhook_url: str | None = None

    # Metrics endpoint auth (for Grafana Cloud scraping)
    metrics_username: str = "metrics"
    metrics_password: str | None = None

    # Port for the server (Railway sets this via PORT env var)
    port: int = 8000

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        # Railway provides postgresql://, we need postgresql+asyncpg://
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    class Config:
        env_file = ".env"


settings = Settings()
