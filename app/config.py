from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    bot_token: str

    openrouter_api_key: str = ""
    jev_model: str = "~typesafe/jev-latest"
    jev_endpoint: str = "https://openrouter.ai/api/alpha/decisions"
    jev_timeout_seconds: float = 25.0
    jev_max_concurrency: int = 6
    openrouter_http_referer: str = ""
    openrouter_title: str = "Jev Telegram Guard"

    database_url: str = "sqlite+aiosqlite:///./data/jev.db"

    default_threshold: float = 0.55
    default_warn_limit: int = 3
    default_mute_minutes: int = 60
    default_flood_messages: int = 7
    default_flood_seconds: int = 10

    default_language: str = "en"
    # Через сколько секунд удалять сообщения бота (0 — не удалять).
    default_self_delete_seconds: int = 0

    # Догон пропущенных сообщений при запуске (за время, пока бот был выключен).
    # Telegram хранит апдейты не старше 24 часов.
    backlog_enabled: bool = True
    backlog_max_age_hours: int = 24
    backlog_limit: int = 200

    log_level: str = "INFO"

    @property
    def jev_enabled(self) -> bool:
        return bool(self.openrouter_api_key.strip())


settings = Settings()
