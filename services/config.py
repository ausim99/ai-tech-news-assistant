"""Central settings, loaded from environment variables (GitHub Secrets / Vercel env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Repo the dashboard reads data from and dispatches workflows against.
    github_repo: str = "ausim99/ai-tech-news-assistant"
    github_token: str = ""
    github_branch: str = "main"

    # CORS: comma-separated list of allowed origins, "*" allows any.
    allowed_origins: str = "*"

    # xAI Grok (OpenAI-compatible chat completions).
    grok_api_key: str = ""
    grok_model: str = "grok-4"

    # DeepSeek (OpenAI-compatible), fallback if Grok fails.
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    # Gemini (via its OpenAI-compatible endpoint), fallback if the above fail.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Telegram Bot API.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Gmail SMTP (App Password auth).
    gmail_address: str = ""
    gmail_app_password: str = ""
    gmail_to_address: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
