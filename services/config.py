"""Central settings, loaded from environment variables (GitHub Secrets / Vercel env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Repo the dashboard reads data from and dispatches workflows against.
    github_repo: str = "owner/ai-tech-news-assistant"
    github_token: str = ""
    github_branch: str = "main"

    # CORS: comma-separated list of allowed origins, "*" allows any.
    allowed_origins: str = "*"

    # xAI Grok (OpenAI-compatible chat completions).
    grok_api_key: str = ""
    grok_model: str = "grok-4"

    # Telegram Bot API.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Meta WhatsApp Cloud API.
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_to_number: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
