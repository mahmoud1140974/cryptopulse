"""Background alert engine for tracked tokens."""

from __future__ import annotations

from typing import Any

from analysis.token_analyzer import TokenAnalyzer
from database.models import Database
from utils.formatters import format_alert_message


class AlertEngine:
    def __init__(self, database: Database, analyzer: TokenAnalyzer, bot: Any | None = None) -> None:
        self.database = database
        self.analyzer = analyzer
        self.bot = bot

    async def check_once(self) -> dict[str, int]:
        items = await self.database.list_all_watchlist()
        checked = 0
        triggered = 0

        for item in items:
            checked += 1
            try:
                snapshot = await self.analyzer.get_market_snapshot(item["contract_address"], item.get("chain"))
                reasons = self._trigger_reasons(item, snapshot)
                avg_volume = _next_average(item.get("avg_volume"), snapshot.get("volume_24h_usd"))
                await self.database.update_watchlist_snapshot(
                    item["id"],
                    snapshot.get("price_usd"),
                    snapshot.get("liquidity_usd"),
                    snapshot.get("volume_24h_usd"),
                    avg_volume,
                )
                if not reasons:
                    continue
                message = format_alert_message(item, snapshot, reasons)
                await self.database.insert_alert(item["telegram_id"], item["id"], "market_movement", message)
                if self.bot is not None:
                    await self.bot.send_message(item["telegram_id"], message, parse_mode="HTML")
                triggered += 1
            except Exception as exc:
                await self.database.log_error(f"Alert check failed for {item.get('id')}: {exc}")

        return {"checked": checked, "triggered": triggered}

    def _trigger_reasons(self, item: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
        reasons: list[str] = []
        price_change = _pct_change(item.get("last_price"), snapshot.get("price_usd"))
        liquidity_change = _pct_change(item.get("last_liquidity"), snapshot.get("liquidity_usd"))
        current_volume = _float(snapshot.get("volume_24h_usd"))
        avg_volume = _float(item.get("avg_volume")) or _float(item.get("last_volume"))

        if price_change is not None and abs(price_change) > 10:
            reasons.append(f"Price changed by {price_change:+.2f}% since the last check")
        if liquidity_change is not None and abs(liquidity_change) > 20:
            reasons.append(f"Liquidity changed by {liquidity_change:+.2f}% since the last check")
        if current_volume is not None and avg_volume and current_volume > avg_volume * 3:
            reasons.append("24h volume is more than 3x the stored average")
        return reasons


def _pct_change(previous: Any, current: Any) -> float | None:
    old = _float(previous)
    new = _float(current)
    if old is None or new is None or old == 0:
        return None
    return (new - old) / old * 100


def _next_average(previous_avg: Any, current: Any) -> float | None:
    old = _float(previous_avg)
    new = _float(current)
    if new is None:
        return old
    if old is None:
        return new
    return (old + new) / 2


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
