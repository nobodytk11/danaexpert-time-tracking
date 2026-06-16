"""Application configuration.

Settings are read from environment variables (with sensible defaults for local
development). Centralising them here keeps the rest of the code free of os.environ
look-ups and makes the app easy to point at PostgreSQL or a real Slack webhook.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite for local/demo. Swap for a postgresql:// URL to run on Postgres –
    # no other code changes are required because we go through SQLAlchemy.
    database_url: str = "sqlite:///./timetracking.db"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Optional. When empty the Slack notifier becomes a safe no-op.
    slack_webhook_url: str = ""


settings = Settings()
