"""Telegram message formatting helpers."""

from __future__ import annotations

import html
from decimal import Decimal, InvalidOperation
from typing import Any

DISCLAIMER = (
    "Crypto assets are highly risky. This tool provides data and risk indicators "
    "for informational purposes only and does not constitute financial advice."
)


def escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def format_money(value: Any) -> str:
    if value is None:
        return "Data unavailable."
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Data unavailable."
    if number >= 1:
        return f"${number:,.2f}"
    return f"${number:,.8f}".rstrip("0").rstrip(".")


def format_number(value: Any) -> str:
    if value is None:
        return "Data unavailable."
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "Data unavailable."


def format_percent(value: Any) -> str:
    if value is None:
        return "Data unavailable."
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "Data unavailable."


def short_address(address: str | None) -> str:
    if not address:
        return "Data unavailable."
    if len(address) <= 14:
        return escape(address)
    return f"{escape(address[:6])}…{escape(address[-4:])}"


def format_token_report(analysis: dict[str, Any]) -> str:
    """Format a token analysis without inventing missing data."""
    risk = analysis.get("risk") or {}
    symbol = analysis.get("symbol") or analysis.get("name") or "Unknown token"
    chain = analysis.get("chain") or "Unknown"
    score = risk.get("score")
    band = risk.get("band") or "Data unavailable."
    emoji = risk.get("emoji") or "⚪"
    reasons = risk.get("reasons") or []

    title = f"{emoji} <b>{escape(str(band)).upper()}</b>"
    if score is not None:
        title += f" — Score {escape(score)}/100"
    title += f"\n<b>{escape(str(symbol))}</b> ({short_address(analysis.get('address'))})"

    reason_lines = ["<b>Reasons:</b>"]
    if reasons:
        reason_lines.extend(f"• {escape(reason)}" for reason in reasons)
    else:
        reason_lines.append("• Data unavailable.")

    data_lines = [
        "",
        "📊 <b>Data:</b>",
        f"Price: {format_money(analysis.get('price_usd'))}",
        f"Liquidity: {format_money(analysis.get('liquidity_usd'))}",
        f"Volume 24h: {format_money(analysis.get('volume_24h_usd'))}",
        f"Market cap: {format_money(analysis.get('market_cap_usd'))}",
        f"Holders: {format_number(analysis.get('holder_count'))}",
        f"Chain: {escape(str(chain))}",
    ]

    return "\n".join([title, "", *reason_lines, *data_lines, "", f"⚠️ {DISCLAIMER}"])


def format_alert_message(item: dict[str, Any], snapshot: dict[str, Any], reasons: list[str]) -> str:
    symbol = item.get("symbol") or snapshot.get("symbol") or "Tracked token"
    reason_text = "\n".join(f"• {escape(reason)}" for reason in reasons) if reasons else "• Data unavailable."
    return "\n".join(
        [
            f"🔔 <b>CryptoPulse Alert</b> — {escape(str(symbol))}",
            "",
            reason_text,
            "",
            f"Price: {format_money(snapshot.get('price_usd'))}",
            f"Liquidity: {format_money(snapshot.get('liquidity_usd'))}",
            f"Volume 24h: {format_money(snapshot.get('volume_24h_usd'))}",
            "",
            f"⚠️ {DISCLAIMER}",
        ]
    )


def decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
