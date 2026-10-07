"""Formatters for Telegram messages."""

import html
escape = html.escape
from typing import Any


def _get(data: dict, *keys, default=None):
    """Cherche la première clé existante parmi keys."""
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return default


def _format_number(val: Any, decimals: int = 2) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if decimals == 8:
            formatted = f"{v:.8f}".rstrip('0').rstrip('.')
            return formatted if formatted else "0"
        return f"{v:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(val)


def _format_int(val: Any) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{int(val):,}"
    except (TypeError, ValueError):
        return str(val)


def _format_tax(tax: Any) -> str:
    """
    Formate une taxe. Accepte :
    - un pourcentage déjà normalisé (ex: 5.0 = 5%)
    - un décimal (ex: 0.05 = 5%)
    """
    if tax is None:
        return "N/A"
    try:
        t = float(tax)
    except (TypeError, ValueError):
        return "N/A"
    # Si la valeur est <= 1, c'est probablement un décimal
    pct = t * 100 if t <= 1 else t
    if pct.is_integer():
        return f"{int(pct)}%"
    return f"{pct:.1f}%"


def _short_address(address: Any) -> str:
    if not address or not isinstance(address, str) or len(address) < 10:
        return str(address or "")
    return f"{address[:6]}…{address[-4:]}"


def format_token_report(analysis: dict[str, Any]) -> str:
    """Formate le rapport d'analyse pour l'affichage Telegram en HTML."""
    risk = analysis.get("risk", {}) or {}
    score = risk.get("score", 0)
    band = risk.get("band") or risk.get("level") or "UNKNOWN"

    if isinstance(band, str):
        band_upper = band.upper().replace("_", " ")
    else:
        band_upper = "UNKNOWN"

    if score >= 75:
        risk_emoji = "🚨"
    elif score >= 50:
        risk_emoji = "⚠️"
    elif score >= 25:
        risk_emoji = "🟡"
    else:
        risk_emoji = "🟢"

    lines = []
    lines.append(f"{risk_emoji} <b>{band_upper} — Score {score}/100</b>")

    symbol = escape(str(analysis.get("symbol") or "UNKNOWN"))
    address = _get(analysis, "contract_address", "address", "token_address", default="")
    short_addr = _short_address(address)
    lines.append(f"<b>${symbol}</b> ({short_addr})\n")

    reasons = risk.get("reasons", []) or []
    if reasons:
        lines.append("📋 <b>Reasons</b>")
        for reason in reasons:
            lines.append(f"• {escape(str(reason))}")
        lines.append("")

    lines.append("📊 <b>Market Data</b>")

    price = _get(analysis, "price_usd", "price")
    if price is not None:
        try:
            p = float(price)
            if p < 0.01:
                lines.append(f"💵 <b>Price:</b> ${_format_number(price, 8)}")
            else:
                lines.append(f"💵 <b>Price:</b> ${_format_number(price, 2)}")
        except (TypeError, ValueError):
            lines.append("💵 <b>Price:</b> N/A")
    else:
        lines.append("💵 <b>Price:</b> N/A")

    liquidity = _get(analysis, "liquidity_usd", "liquidity")
    lines.append(f"💧 <b>Liquidity:</b> ${_format_number(liquidity)}")

    volume = _get(analysis, "volume_24h_usd", "volume_24h", "volume")
    lines.append(f"📈 <b>Volume 24h:</b> ${_format_number(volume)}")

    mcap = _get(analysis, "market_cap_usd", "market_cap", "mcap")
    lines.append(f"🏦 <b>Market Cap:</b> ${_format_number(mcap)}")

    holders = _get(
        analysis,
        "holder_count",
        "holders_count",
        "holders",
        "total_holders",
    )
    lines.append(f"👥 <b>Holders:</b> {_format_int(holders)}")

    chain_raw = analysis.get("chain", "unknown")
    chain = chain_raw.capitalize() if isinstance(chain_raw, str) else "Unknown"
    lines.append(f"⛓ <b>Chain:</b> {chain}")

    is_honeypot = _get(analysis, "is_honeypot", "honeypot")
    if is_honeypot is not None:
        if is_honeypot:
            lines.append("🍯 <b>Honeypot:</b> YES 🚨 DO NOT TRADE")
        else:
            lines.append("🍯 <b>Honeypot:</b> No ✅")

    # Cherche d'abord la version déjà en %, puis la version brute
    buy_tax = _get(analysis, "buy_tax_pct", "buy_tax", "buy_fee")
    sell_tax = _get(analysis, "sell_tax_pct", "sell_tax", "sell_fee")
    if buy_tax is not None or sell_tax is not None:
        lines.append(
            f"💰 <b>Buy/Sell tax:</b> {_format_tax(buy_tax)} / {_format_tax(sell_tax)}"
        )

    is_renounced = _get(
        analysis,
        "is_renounced",
        "ownership_renounced",
        "renounced",
    )
    owner_addr = _get(analysis, "owner_address", "owner")
    if is_renounced is not None:
        if is_renounced:
            lines.append("👑 <b>Ownership:</b> Renounced ✅")
        else:
            short_owner = _short_address(owner_addr) or "Unknown"
            lines.append(
                f"👑 <b>Ownership:</b> NOT renounced ⚠️ (owner: {short_owner})"
            )

    if str(chain_raw).lower() == "solana":
        freeze_auth = _get(analysis, "freeze_authority")
        if freeze_auth:
            lines.append("🥶 <b>Freeze Authority:</b> Active ⚠️")
        else:
            lines.append("🥶 <b>Freeze Authority:</b> Disabled ✅")

    lines.append(
        "\n⚠️ <i>Crypto assets are highly risky. Always do your own research before trading.</i>"
    )

    return "\n".join(lines)


def format_alert_message(
    item: dict[str, Any],
    snapshot: dict[str, Any],
    reasons: list[str],
) -> str:
    """Formate un message d'alerte Telegram en HTML premium."""
    symbol = escape(str(item.get("symbol") or "TOKEN"))
    address = item.get("contract_address") or item.get("address") or ""
    short_addr = _short_address(address)
    chain_raw = item.get("chain") or "unknown"
    chain = chain_raw.capitalize() if isinstance(chain_raw, str) else "Unknown"

    lines = []
    lines.append("🚨 <b>TOKEN ALERT</b>\n")
    lines.append(f"<b>${symbol}</b> ({short_addr})")
    lines.append(f"⛓ <b>Chain:</b> {chain}\n")

    if reasons:
        lines.append("📋 <b>Reasons</b>")
        for reason in reasons:
            lines.append(f"• {escape(str(reason))}")
        lines.append("")

    lines.append("📊 <b>Current Snapshot</b>")
    lines.append(f"💵 <b>Price:</b> ${_format_number(snapshot.get('price_usd'), 8)}")
    lines.append(f"💧 <b>Liquidity:</b> ${_format_number(snapshot.get('liquidity_usd'))}")
    lines.append(f"📈 <b>Volume 24h:</b> ${_format_number(snapshot.get('volume_24h_usd'))}")

    lines.append("\n⚠️ <i>This is not financial advice. Verify independently before acting.</i>")

    return "\n".join(lines)
