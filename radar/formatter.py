"""Radar formatter — builds Telegram posts for the radar channel."""

from __future__ import annotations

import html
from typing import Any


def _escape(text: Any) -> str:
    return html.escape(str(text or ""), quote=False)


def _money(val: Any) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v / 1_000:.1f}K"
    if v >= 1:
        return f"${v:,.2f}"
    return f"${v:.8f}".rstrip("0").rstrip(".")


def _pct(val: Any) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def _age(pair_created_at_ms: int | None) -> str:
    import time
    if not pair_created_at_ms:
        return "?"
    hours = max((time.time() * 1000 - pair_created_at_ms) / 3_600_000, 0)
    if hours < 1:
        return f"{int(hours * 60)}min"
    return f"{hours:.1f}h"


def _short(address: str | None) -> str:
    if not address or len(address) < 12:
        return address or ""
    return f"{address[:6]}…{address[-4:]}"


def _chain_label(chain: str | None) -> str:
    mapping = {
        "ethereum": "Ethereum",
        "solana": "Solana",
        "bsc": "BSC",
        "base": "Base",
        "polygon": "Polygon",
        "arbitrum": "Arbitrum",
    }
    return mapping.get(str(chain or "").lower(), str(chain or "?").capitalize())


def _signal_emoji(signal: str) -> str:
    return {
        "BUY": "🟢",
        "WATCH": "🟡",
        "AVOID": "🔴",
    }.get(signal, "⚪")


def format_new_token_post(
    analysis: dict[str, Any],
    signal: str,
    bot_username: str = "CryptoPulse113_bot",
) -> str:
    """
    Format du post principal 'nouveau memecoin détecté'.
    """
    symbol = _escape(analysis.get("symbol") or "UNKNOWN")
    address = analysis.get("address") or ""
    chain = _chain_label(analysis.get("chain"))

    price = _money(analysis.get("price_usd"))
    liquidity = _money(analysis.get("liquidity_usd"))
    volume = _money(analysis.get("volume_24h_usd"))
    mcap = _money(analysis.get("market_cap_usd"))
    holders = analysis.get("holder_count")
    top10 = analysis.get("top10_holder_pct")
    risk = (analysis.get("risk") or {}).get("score")

    age = _age(analysis.get("pair_created_at"))

    risk_emoji = "🟢" if (risk or 100) <= 20 else "🟡" if (risk or 100) <= 45 else "🟠"
    signal_emoji = _signal_emoji(signal)

    lines = []
    lines.append(f"⚡ <b>NEW</b> — <b>${symbol}</b>")
    lines.append(f"⛓ {chain} • ⏱ {age} old")
    lines.append("")

    lines.append(f"💵 <b>Price:</b> {price}")
    lines.append(f"💧 <b>Liquidity:</b> {liquidity}")
    if volume != "N/A":
        lines.append(f"📈 <b>Volume 24h:</b> {volume}")
    if mcap != "N/A":
        lines.append(f"🏦 <b>Market Cap:</b> {mcap}")
    if holders is not None:
        lines.append(f"👥 <b>Holders:</b> {_escape(holders)}")
    if top10 is not None:
        lines.append(f"👑 <b>Top 10:</b> {_pct(top10)}")
    lines.append("")

    lines.append(f"📊 <b>Risk:</b> {risk_emoji} {risk}/100")
    lines.append(f"🎯 <b>Signal:</b> {signal_emoji} <b>{signal}</b>")
    lines.append("")

    lines.append(f"🔢 <code>{_escape(address)}</code>")
    lines.append("")
    lines.append(f"🔍 Scan any token free → @{_escape(bot_username)}")
    lines.append("")
    lines.append("⚠️ <i>Not financial advice. DYOR.</i>")

    return "\n".join(lines)


def format_update_post(
    token: dict[str, Any],
    current: dict[str, Any],
    hours: int,
) -> str | None:
    """
    Format du post 'update' — compare le prix/liquidité d'origine avec
    la valeur actuelle.
    Renvoie None si on n'a pas les données nécessaires.
    """
    initial_price = token.get("initial_price")
    initial_liquidity = token.get("initial_liquidity")
    current_price = current.get("price_usd")
    current_liquidity = current.get("liquidity_usd")
    current_holders = current.get("holder_count")

    if initial_price is None or current_price is None or initial_price == 0:
        return None

    price_change = ((current_price - initial_price) / initial_price) * 100
    liq_change = None
    if initial_liquidity and current_liquidity:
        liq_change = ((current_liquidity - initial_liquidity) / initial_liquidity) * 100

    symbol = _escape(token.get("symbol") or "UNKNOWN")
    signal = token.get("signal") or "?"
    signal_emoji = _signal_emoji(signal)

    arrow = "📈" if price_change >= 0 else "📉"

    lines = []
    lines.append(f"{arrow} <b>UPDATE</b> — <b>${symbol}</b> ({hours}h later)")
    lines.append("")
    lines.append(f"💵 <b>Price:</b> {_money(initial_price)} → {_money(current_price)}")
    lines.append(f"   <b>{price_change:+.1f}%</b>")
    if liq_change is not None:
        lines.append(f"💧 <b>Liquidity:</b> {_money(initial_liquidity)} → {_money(current_liquidity)}")
        lines.append(f"   <b>{liq_change:+.1f}%</b>")
    if current_holders:
        lines.append(f"👥 <b>Holders:</b> {_escape(current_holders)}")
    lines.append("")
    lines.append(f"🎯 Signal was: {signal_emoji} <b>{signal}</b>")
    lines.append("")
    lines.append("⚠️ <i>Not financial advice. DYOR.</i>")

    return "\n".join(lines)


def format_daily_recap(
    tokens: list[dict[str, Any]],
    stats: dict[str, int],
    bot_username: str = "CryptoPulse113_bot",
) -> str:
    """Récap quotidien en fin de journée."""
    lines = []
    lines.append("🔥 <b>TOP MEMECOINS TODAY</b>")
    lines.append("")

    if not tokens:
        lines.append("<i>No qualifying tokens today.</i>")
    else:
        for i, t in enumerate(tokens[:5], start=1):
            symbol = _escape(t.get("symbol") or "?")
            signal = t.get("signal") or "?"
            emoji = _signal_emoji(signal)
            lines.append(f"{i}. {emoji} <b>${symbol}</b> — {signal}")

    lines.append("")
    lines.append("📊 <b>Today's stats</b>")
    lines.append(f"• Scanned: <b>{stats.get('scanned', 0)}</b>")
    lines.append(f"• Passed filters: <b>{stats.get('posted', 0)}</b>")
    lines.append(f"• BUY signals: <b>{stats.get('buy', 0)}</b>")
    lines.append("")
    lines.append(f"🔍 Scan any token free → @{_escape(bot_username)}")
    lines.append("")
    lines.append("⚠️ <i>Not financial advice. DYOR.</i>")

    return "\n".join(lines)


def format_daily_stats(stats: dict[str, int], bot_username: str = "CryptoPulse113_bot") -> str:
    """Stats du matin — bilan de la veille."""
    lines = []
    lines.append("📊 <b>RADAR STATS — YESTERDAY</b>")
    lines.append("")
    lines.append(f"🆕 Tokens scanned: <b>{stats.get('scanned', 0)}</b>")
    lines.append(f"✅ Passed filters: <b>{stats.get('posted', 0)}</b>")
    lines.append(f"🟢 BUY signals: <b>{stats.get('buy', 0)}</b>")
    lines.append(f"🟡 WATCH signals: <b>{stats.get('watch', 0)}</b>")
    lines.append(f"🔴 AVOID signals: <b>{stats.get('avoid', 0)}</b>")
    lines.append("")
    lines.append(f"🔍 Scan any token free → @{_escape(bot_username)}")
    lines.append("")
    lines.append("⚠️ <i>Not financial advice. DYOR.</i>")

    return "\n".join(lines)


def format_tip_of_the_day() -> str:
    """Tip quotidien — éducatif."""
    import random

    tips = [
        "Liquidity under $20K + top 10 holders over 70% = 90% chance of rug. Skip it.",
        "Always check if ownership is renounced. Active owner = can change taxes anytime.",
        "Honeypot = you can buy but you can't sell. Check before you buy.",
        "Top 10 holders control >50%? One whale dump and you're liquidated.",
        "A token less than 24h old with no liquidity lock is a red flag.",
        "If the contract is not verified, the source code is hidden. Skip it.",
        "Freeze authority on Solana = the dev can freeze your tokens. Always check.",
        "High buy/sell tax (>10%) = you lose money on every trade. Avoid.",
    ]
    return "🎓 <b>TIP OF THE DAY</b>\n\n" + random.choice(tips)
