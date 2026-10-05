"""Handler-facing formatting, rate limiting, and database tests."""

from __future__ import annotations

from bot.middlewares import RateLimiter
from config import Settings
from database.models import Database
from utils.formatters import DISCLAIMER, format_token_report


def test_token_report_handles_missing_data() -> None:
    text = format_token_report({"address": "0x" + "a" * 40, "risk": {"score": None, "band": None, "emoji": None, "reasons": []}})
    assert "Data unavailable." in text
    assert DISCLAIMER in text


def test_rate_limiter_blocks_excess_calls() -> None:
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow(123) is True
    assert limiter.allow(123) is True
    assert limiter.allow(123) is False
    assert limiter.allow(456) is True


async def test_database_watchlist_crud(tmp_path) -> None:
    settings = Settings(sqlite_path=str(tmp_path / "cryptopulse-test.db"))
    db = Database(settings)
    await db.init_schema()

    user = await db.get_or_create_user(12345)
    assert user["telegram_id"] == 12345
    assert user["plan"] == "free"

    item = await db.add_watchlist(12345, "ethereum", "0x" + "a" * 40, symbol="TEST", name="Test Token")
    assert await db.count_watchlist(12345) == 1

    items = await db.list_watchlist(12345)
    assert items[0]["symbol"] == "TEST"

    await db.update_watchlist_snapshot(item["id"], 1.0, 10_000.0, 500.0, 500.0)
    updated = await db.get_watchlist_item(item["id"])
    assert updated["last_price"] == 1.0
    assert updated["last_liquidity"] == 10_000.0

    await db.insert_alert(12345, item["id"], "test_alert", "Test alert message")
    alerts = await db.list_alerts(12345)
    assert alerts[0]["message"] == "Test alert message"

    await db.remove_watchlist(12345, item["id"])
    assert await db.count_watchlist(12345) == 0
