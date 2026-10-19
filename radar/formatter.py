"""Radar formatter — builds Telegram posts for the radar channel."""

from __future__ import annotations

import html
from typing import Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    try:
        if pair_created_at_ms < 10_000_000_000:
            pair_created_at_ms = pair_created_at_ms * 1000
        hours = max((time.time() * 1000 - pair_created_at_ms) / 3_600_000, 0)
        if hours < 1:
            return f"{int(hours * 60)}min"
        return f"{hours:.1f}h"
    except Exception:
        return "?"

def _chain_label(chain: str | None) -> str:
    mapping = {"ethereum": "Ethereum", "solana": "Solana", "bsc": "BSC", "base": "Base"}
    return mapping.get(str(chain or "").lower(), str(chain or "?").capitalize())

def _signal_emoji(signal: str) -> str:
    return {"BUY": "🟢", "WATCH": "🟡", "AVOID": "🔴"}.get(signal, "⚪")

def format_new_token_post(analysis: dict[str, Any], signal: str, bot_username: str = "CryptoPulse113_bot") -> str:
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
    reply_count = analysis.get("reply_count", 0)
    age = _age(analysis.get("pair_created_at"))
    signal_emoji = _signal_emoji(signal)

    lines = [
        f"⚡ <b>NEW</b> — <b>${symbol}</b>",
        f"⛓ {chain} • ⏱ {age} old",
        "",
        f"💵 <b>Price:</b> {price}"
    ]
    if liquidity != "N/A": lines.append(f"💧 <b>Liquidity:</b> {liquidity}")
    if volume != "N/A": lines.append(f"📈 <b>Volume 24h:</b> {volume}")
    lines.append(f"🏦 <b>Market Cap:</b> {mcap}")
    if reply_count > 0: lines.append(f"💬 <b>Hype:</b> {reply_count} comments")
    if holders is not None: lines.append(f"👥 <b>Holders:</b> {_escape(holders)}")
    if top10 is not None: lines.append(f"👑 <b>Top 10:</b> {_pct(top10)}")
    
    lines.append("")
    if risk is not None:
        risk_emoji = "🟢" if risk <= 20 else "🟡" if risk <= 45 else "🟠"
        lines.append(f"📊 <b>Risk:</b> {risk_emoji} {risk}/100")
    lines.extend([
        f"🎯 <b>Signal:</b> {signal_emoji} <b>{signal}</b>",
        "",
        f"🔢 <code>{_escape(address)}</code>",
        "",
        f"🔍 Scan any token free → @{_escape(bot_username)}",
        "",
        "⚠️ <i>Not financial advice. DYOR.</i>"
    ])
    return "\n".join(lines)

def format_update_post(token: dict[str, Any], current: dict[str, Any], hours: int) -> str | None:
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

    lines = [
        f"{arrow} <b>UPDATE</b> — <b>${symbol}</b> ({hours}h later)",
        "",
        f"💵 <b>Price:</b> {_money(initial_price)} → {_money(current_price)}",
        f"   <b>{price_change:+.1f}%</b>"
    ]
    if liq_change is not None:
        lines.append(f"💧 <b>Liquidity:</b> {_money(initial_liquidity)} → {_money(current_liquidity)}")
        lines.append(f"   <b>{liq_change:+.1f}%</b>")
    if current_holders:
        lines.append(f"👥 <b>Holders:</b> {_escape(current_holders)}")
    lines.extend([
        "",
        f"🎯 Signal was: {signal_emoji} <b>{signal}</b>",
        "",
        "⚠️ <i>Not financial advice. DYOR.</i>"
    ])
    return "\n".join(lines)

def format_pump_alert(token: dict[str, Any], current: dict[str, Any], multiplier: float) -> str | None:
    initial_mcap = token.get("initial_market_cap") or token.get("market_cap_usd")
    current_mcap = current.get("market_cap_usd")
    
    if not initial_mcap or not current_mcap:
        return None
        
    symbol = _escape(token.get("symbol") or "UNKNOWN")
    address = token.get("contract_address") or ""
    
    lines = []
    if multiplier >= 10:
        lines.append(f"🚀🔥 <b>MASSIVE PUMP: x{multiplier:.0f} REACHED!</b> 🔥🚀")
    elif multiplier >= 5:
        lines.append(f"🚀 <b>PUMP ALERT: x{multiplier:.0f} REACHED!</b> 🚀")
    else:
        lines.append(f"📈 <b>PUMP ALERT: x{multiplier:.0f} REACHED!</b> 📈")
        
    lines.extend([
        f"<b>${symbol}</b> is exploding right now!",
        "",
        f"🏦 <b>Initial Market Cap:</b> {_money(initial_mcap)}",
        f"🚀 <b>Current Market Cap:</b> {_money(current_mcap)}",
        f"📊 <b>Performance:</b> +{(multiplier - 1) * 100:.0f}%",
        "",
        f"🔢 <code>{_escape(address)}</code>",
        "",
        "This token was called earlier by CryptoPulse Radar. Did you catch it? 👀",
        f"🔍 Scan any token free → @CryptoPulse113_bot",
        "",
        "⚠️ <i>Not financial advice. DYOR.</i>"
    ])
    return "\n".join(lines)

def format_daily_recap(tokens: list[dict[str, Any]], stats: dict[str, int], bot_username: str = "CryptoPulse113_bot") -> str:
    lines = ["🔥 <b>TOP MEMECOINS TODAY</b>", ""]
    if not tokens: lines.append("<i>No qualifying tokens today.</i>")
    else:
        for i, t in enumerate(tokens[:5], start=1):
            lines.append(f"{i}. {_signal_emoji(t.get('signal'))} <b>${_escape(t.get('symbol'))}</b> — {t.get('signal')}")
    lines.extend([
        "", "📊 <b>Today's stats</b>",
        f"• Scanned: <b>{stats.get('scanned', 0)}</b>",
        f"• Passed filters: <b>{stats.get('posted', 0)}</b>",
        f"• BUY signals: <b>{stats.get('buy', 0)}</b>",
        "", f"🔍 Scan any token free → @{_escape(bot_username)}", "", "⚠️ <i>Not financial advice. DYOR.</i>"
    ])
    return "\n".join(lines)

def format_daily_stats(stats: dict[str, int], bot_username: str = "CryptoPulse113_bot") -> str:
    lines = [
        "📊 <b>RADAR STATS — YESTERDAY</b>", "",
        f"🆕 Tokens scanned: <b>{stats.get('scanned', 0)}</b>",
        f"✅ Passed filters: <b>{stats.get('posted', 0)}</b>",
        f"🟢 BUY signals: <b>{stats.get('buy', 0)}</b>",
        f"🟡 WATCH signals: <b>{stats.get('watch', 0)}</b>",
        f"🔴 AVOID signals: <b>{stats.get('avoid', 0)}</b>",
        "", f"🔍 Scan any token free → @{_escape(bot_username)}", "", "⚠️ <i>Not financial advice. DYOR.</i>"
    ]
    return "\n".join(lines)

def format_tip_of_the_day() -> str:
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

def build_sniper_keyboard(analysis: dict[str, Any]) -> InlineKeyboardMarkup:
    address = analysis.get("address")
    chain = str(analysis.get("chain") or "ethereum").lower()
    buttons = []
    dex_url = f"https://dexscreener.com/{chain}/{address}"
    buttons.append([InlineKeyboardButton(text="📊 View Chart (DexScreener)", url=dex_url)])
    if chain == "solana":
        buttons.append([InlineKeyboardButton(text="🎯 Snipe on Jupiter", url=f"https://jup.ag/swap/SOL-{address}")])
    elif chain in ("ethereum", "eth"):
        buttons.append([InlineKeyboardButton(text="🎯 Buy on Uniswap", url=f"https://app.uniswap.org/#/swap?outputCurrency={address}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
