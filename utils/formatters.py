"""Formatters for Telegram messages."""

import html
from typing import Any


def _format_number(val: Any, decimals: int = 2) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        # Pour les très petits nombres, on garde jusqu'à 8 décimales sans trailing zeros
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


def _format_tax(tax: float | None) -> str:
    if tax is None:
        return "N/A"
    # GoPlus retourne souvent en décimal (ex: 0.05 pour 5%)
    pct = tax * 100 if tax < 1 else tax
    if pct.is_integer():
        return f"{int(pct)}%"
    return f"{pct:.1f}%"


def format_token_report(analysis: dict[str, Any]) -> str:
    """Formate le rapport d'analyse pour l'affichage Telegram en HTML."""
    risk = analysis.get("risk", {})
    score = risk.get("score", 0)
    risk_level = risk.get("level", "UNKNOWN")

    # Header Risk
    if score >= 75:
        risk_emoji = "🚨"
    elif score >= 50:
        risk_emoji = "⚠️"
    else:
        risk_emoji = "✅"

    lines = []
    lines.append(f"{risk_emoji} <b>{risk_level.upper()} RISK — Score {score}/100</b>")

    symbol = html.escape(analysis.get("symbol") or "UNKNOWN")
    address = analysis.get("contract_address") or analysis.get("address") or ""
    short_addr = f"{address[:6]}…{address[-4:]}" if address and len(address) > 10 else address
    lines.append(f"<b>${symbol}</b> ({short_addr})\n")

    # Reasons
    reasons = risk.get("reasons", [])
    if reasons:
        lines.append("📋 <b>Reasons</b>")
        for reason in reasons:
            lines.append(f"• {html.escape(str(reason))}")
        lines.append("")

    # Market Data
    lines.append("📊 <b>Market Data</b>")

    price = analysis.get("price_usd")
    if price is not None:
        p = float(price)
        if p < 0.01:
            lines.append(f"💵 <b>Price:</b> ${_format_number(price, 8)}")
        else:
            lines.append(f"💵 <b>Price:</b> ${_format_number(price, 2)}")
    else:
        lines.append("💵 <b>Price:</b> N/A")

    liquidity = analysis.get("liquidity_usd")
    lines.append(f"💧 <b>Liquidity:</b> ${_format_number(liquidity)}")

    volume = analysis.get("volume_24h")
    lines.append(f"📈 <b>Volume 24h:</b> ${_format_number(volume)}")

    mcap = analysis.get("market_cap")
    lines.append(f"🏦 <b>Market Cap:</b> ${_format_number(mcap)}")

    # BUG 3: Holders
    holder_count = analysis.get("holder_count")
    lines.append(f"👥 <b>Holders:</b> {_format_int(holder_count)}")

    # Chain
    chain_raw = analysis.get("chain", "unknown")
    chain = chain_raw.capitalize() if isinstance(chain_raw, str) else "Unknown"
    lines.append(f"⛓ <b>Chain:</b> {chain}")

    # BUG 4: Honeypot & Taxes
    is_honeypot = analysis.get("is_honeypot")
    if is_honeypot is not None:
        if is_honeypot:
            lines.append("🍯 <b>Honeypot:</b> YES 🚨 DO NOT TRADE")
        else:
            lines.append("🍯 <b>Honeypot:</b> No ✅")

    buy_tax = analysis.get("buy_tax")
    sell_tax = analysis.get("sell_tax")
    if buy_tax is not None or sell_tax is not None:
        lines.append(f"💰 <b>Buy/Sell tax:</b> {_format_tax(buy_tax)} / {_format_tax(sell_tax)}")

    # BUG 1: Ownership
    is_renounced = analysis.get("is_renounced")
    owner_addr = analysis.get("owner_address")
    if is_renounced is not None:
        if is_renounced:
            lines.append("👑 <b>Ownership:</b> Renounced ✅")
        else:
            short_owner = f"{owner_addr[:6]}…{owner_addr[-4:]}" if owner_addr and len(owner_addr) > 10 else (owner_addr or "Unknown")
            lines.append(f"👑 <b>Ownership:</b> NOT renounced ⚠️ (owner: {short_owner})")

    # BUG 2: Freeze authority (Solana only)
    if str(chain_raw).lower() == "solana":
        freeze_auth = analysis.get("freeze_authority")
        if freeze_auth:
            lines.append("🥶 <b>Freeze Authority:</b> Active ⚠️")
        else:
            lines.append("🥶 <b>Freeze Authority:</b> Disabled ✅")

    lines.append("\n⚠️ <i>Crypto assets are highly risky. Always do your own research before trading.</i>")

    return "\n".join(lines)
