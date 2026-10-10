"""Formatters for Telegram messages (multilingual)."""

from __future__ import annotations

import html
from typing import Any

escape = html.escape


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
    """Formate une taxe (accepte décimal ou pourcentage)."""
    if tax is None:
        return "N/A"
    try:
        t_val = float(tax)
    except (TypeError, ValueError):
        return "N/A"
    pct = t_val * 100 if t_val <= 1 else t_val
    if pct.is_integer():
        return f"{int(pct)}%"
    return f"{pct:.1f}%"


def _short_address(address: Any) -> str:
    if not address or not isinstance(address, str) or len(address) < 10:
        return str(address or "")
    return f"{address[:6]}…{address[-4:]}"


def _escape_link_label(text: str) -> str:
    """Échappe le texte pour l'affichage dans <a>...</a>."""
    return html.escape(str(text or ""), quote=False)


def format_token_report(analysis: dict[str, Any], lang: str = "en") -> str:
    """Formate le rapport d'analyse pour l'affichage Telegram en HTML."""
    from locales import t

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

    # --- Raisons ---
    reasons = risk.get("reasons", []) or []
    if reasons:
        lines.append(t("report_reasons", lang))
        for reason in reasons:
            lines.append(f"• {escape(str(reason))}")
        lines.append("")

    # --- Données de marché ---
    lines.append(t("report_market_data", lang))

    price = _get(analysis, "price_usd", "price")
    if price is not None:
        try:
            p = float(price)
            if p < 0.01:
                lines.append(t("report_price", lang, value=f"${_format_number(price, 8)}"))
            else:
                lines.append(t("report_price", lang, value=f"${_format_number(price, 2)}"))
        except (TypeError, ValueError):
            lines.append(t("report_price", lang, value="N/A"))
    else:
        lines.append(t("report_price", lang, value="N/A"))

    liquidity = _get(analysis, "liquidity_usd", "liquidity")
    lines.append(t("report_liquidity", lang, value=_format_number(liquidity)))

    volume = _get(analysis, "volume_24h_usd", "volume_24h", "volume")
    lines.append(t("report_volume", lang, value=_format_number(volume)))

    mcap = _get(analysis, "market_cap_usd", "market_cap", "mcap")
    lines.append(t("report_market_cap", lang, value=_format_number(mcap)))

    holders = _get(
        analysis,
        "holder_count",
        "holders_count",
        "holders",
        "total_holders",
    )
    lines.append(t("report_holders", lang, value=_format_int(holders)))

    # --- NOUVEAU : Total Supply ---
    supply = _get(analysis, "total_supply")
    if supply is not None:
        lines.append(t("report_supply", lang, value=_format_int(supply)))

    # --- NOUVEAU : Decimals ---
    decimals = _get(analysis, "decimals")
    if decimals is not None:
        lines.append(t("report_decimals", lang, value=_format_int(decimals)))

    chain_raw = analysis.get("chain", "unknown")
    chain = chain_raw.capitalize() if isinstance(chain_raw, str) else "Unknown"
    lines.append(t("report_chain", lang, value=chain))

    # --- Indicateurs conditionnels ---
    is_honeypot = _get(analysis, "is_honeypot", "honeypot")
    if is_honeypot is not None:
        if is_honeypot:
            lines.append(t("report_honeypot_yes", lang))
        else:
            lines.append(t("report_honeypot_no", lang))

    buy_tax = _get(analysis, "buy_tax_pct", "buy_tax", "buy_fee")
    sell_tax = _get(analysis, "sell_tax_pct", "sell_tax", "sell_fee")
    if buy_tax is not None or sell_tax is not None:
        lines.append(
            t(
                "report_taxes",
                lang,
                buy=_format_tax(buy_tax),
                sell=_format_tax(sell_tax),
            )
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
            lines.append(t("report_ownership_renounced", lang))
        else:
            short_owner = _short_address(owner_addr) or "Unknown"
            lines.append(t("report_ownership_not_renounced", lang, owner=short_owner))

    if str(chain_raw).lower() == "solana":
        freeze_auth = _get(analysis, "freeze_authority_active", "freeze_authority")
        if freeze_auth is True:
            lines.append(t("report_freeze_active", lang))
        elif freeze_auth is False:
            lines.append(t("report_freeze_disabled", lang))

    # --- NOUVEAU : Liens ---
    website = _get(analysis, "website_url")
    twitter = _get(analysis, "twitter_url")
    telegram = _get(analysis, "telegram_url")
    dexscreener = _get(analysis, "dexscreener_url")

    links_lines = []
    if website:
        links_lines.append(f'🌐 <a href="{escape(website)}">{_escape_link_label(t("report_link_website", lang))}</a>')
    if twitter:
        links_lines.append(f'🐦 <a href="{escape(twitter)}">{_escape_link_label(t("report_link_twitter", lang))}</a>')
    if telegram:
        links_lines.append(f'📢 <a href="{escape(telegram)}">{_escape_link_label(t("report_link_telegram", lang))}</a>')
    if dexscreener:
        links_lines.append(f'📊 <a href="{escape(dexscreener)}">{_escape_link_label(t("report_link_dexscreener", lang))}</a>')

    if links_lines:
        lines.append("")
        lines.append(t("report_links", lang))
        for l in links_lines:
            lines.append(l)

    lines.append(t("report_disclaimer", lang))

    return "\n".join(lines)


def format_alert_message(
    item: dict[str, Any],
    snapshot: dict[str, Any],
    reasons: list[str],
    lang: str = "en",
) -> str:
    """Formate un message d'alerte Telegram en HTML."""
    from locales import t

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
        lines.append(t("report_reasons", lang))
        for reason in reasons:
            lines.append(f"• {escape(str(reason))}")
        lines.append("")

    lines.append(t("report_market_data", lang))
    lines.append(t("report_price", lang, value=f"${_format_number(snapshot.get('price_usd'), 8)}"))
    lines.append(t("report_liquidity", lang, value=_format_number(snapshot.get("liquidity_usd"))))
    lines.append(t("report_volume", lang, value=_format_number(snapshot.get("volume_24h_usd"))))

    lines.append("\n⚠️ <i>" + t("not_financial_advice", lang) + "</i>")

    return "\n".join(lines)
