"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent


@dataclass(slots=True)
class Settings:
    bot_token: str | None = None
    etherscan_api_key: str | None = None
    helius_api_key: str | None = None
    coingecko_api_key: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    admin_telegram_id: int | None = None
    free_scan_limit: int = 10
    free_watchlist_limit: int = 5
    free_alert_interval_minutes: int = 15
    log_level: str = "INFO"
    sqlite_path: str = str(BASE_DIR / "cryptopulse.db")
    bot_mode: str = "polling"
    webhook_url: str | None = None
    port: int = 10000

    @classmethod
    def from_env(cls, env_file: str | os.PathLike[str] | None = None) -> "Settings":
        load_dotenv(env_file or BASE_DIR / ".env")
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        return cls(
            bot_token=os.getenv("BOT_TOKEN"),
            etherscan_api_key=os.getenv("ETHERSCAN_API_KEY"),
            helius_api_key=os.getenv("HELIUS_API_KEY"),
            coingecko_api_key=os.getenv("COINGECKO_API_KEY"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
            admin_telegram_id=int(admin_id) if admin_id else None,
            free_scan_limit=_int_env("FREE_SCAN_LIMIT", 10),
            free_watchlist_limit=_int_env("FREE_WATCHLIST_LIMIT", 5),
            free_alert_interval_minutes=_int_env("FREE_ALERT_INTERVAL_MINUTES", 15),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            sqlite_path=os.getenv("SQLITE_PATH", str(BASE_DIR / "cryptopulse.db")),
            bot_mode=os.getenv("BOT_MODE", "polling").lower(),
            webhook_url=os.getenv("WEBHOOK_URL"),
            port=_int_env("PORT", 10000),
        )

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def etherscan_configured(self) -> bool:
        return bool(self.etherscan_api_key)

    @property
    def helius_configured(self) -> bool:
        return bool(self.helius_api_key)

    def require_bot_token(self) -> None:
        if not self.bot_token:
            raise RuntimeError(
                "BOT_TOKEN is missing. Create a .env file from .env.example and add your Telegram bot token."
            )
        if self.bot_mode not in {"polling", "webhook"}:
            raise RuntimeError("BOT_MODE must be either 'polling' or 'webhook'.")
        if self.bot_mode == "webhook" and not self.webhook_url:
            raise RuntimeError("WEBHOOK_URL is required when BOT_MODE=webhook.")


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default
