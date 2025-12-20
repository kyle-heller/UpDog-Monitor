from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/updog_dev"
    )

    # Discord webhook for alerts (optional - alerts disabled if not set)
    # Get this from Discord: Server Settings → Integrations → Webhooks → New Webhook
    discord_webhook_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
