"""Radar filter — applies quality criteria to new tokens.

Objectif : trouver les tokens qui viennent de lancer MAIS qui n'ont PAS
encore explosé, dans la "golden zone" de market cap (40K-200K).
"""

from __future__ import annotations

import time
from typing import Any

# --- Filtres de base ---
MIN_LIQUIDITY_USD = 30_000
MIN_AGE_HOURS = 1.0
MAX_AGE_HOURS = 6.0
MIN_HOLDERS = 100
MAX_TOP10_PCT = 60
MAX_RISK_SCORE = 40

# --- Filtre MARKET CAP (la golden zone) ---
# En dessous : trop risqué (rug en 5 min)
# Au-dessus : déjà pumpé (pas de potentiel)
MIN_MCAP_USD = 40_000
MAX_MCAP_USD = 200_000

# --- Filtres ANTI-PUMP ---
# On ne poste PAS un token qui a déjà fait une grosse variation.
MAX_PRICE_CHANGE_H1 = 50.0
MAX_PRICE_CHANGE_H6 = 100.0
MAX_PRICE_CHANGE_H24 = 200.0


def calculate_age_hours(pair_created_at_ms: int | None) -> float | None:
    if not pair_created_at_ms:
        return None
    return max((time.time() * 1000 - pair_created_at_ms) / 3_600_000, 0)


def apply_filters(analysis: dict[str, Any]) -> tuple[bool, str]:
    """
    Returns (passed: bool, reason: str).
    Si passed=True, reason est vide.
    """
    liquidity = analysis.get("liquidity_usd") or 0
    mcap = analysis.get("market_cap_usd")
    holders = analysis.get("holder_count") or 0
    top10 = analysis.get("top10_holder_pct")
    risk = (analysis.get("risk") or {}).get("score")
    age_hours = calculate_age_hours(analysis.get("pair_created_at"))

    # --- Anti-pump : on refuse les tokens déjà explosés ---
    change_h1 = analysis.get("price_change_h1")
    change_h6 = analysis.get("price_change_h6")
    change_h24 = analysis.get("price_change_h24")

    if change_h1 is not None and change_h1 > MAX_PRICE_CHANGE_H1:
        return False, f"already pumped +{change_h1:.0f}% in 1h"
    if change_h6 is not None and change_h6 > MAX_PRICE_CHANGE_H6:
        return False, f"already pumped +{change_h6:.0f}% in 6h"
    if change_h24 is not None and change_h24 > MAX_PRICE_CHANGE_H24:
        return False, f"already pumped +{change_h24:.0f}% in 24h"

    # --- Filtre MARKET CAP (golden zone) ---
    if mcap is None:
        return False, "market cap unknown"
    if mcap < MIN_MCAP_USD:
        return False, f"mcap ${mcap:.0f} < ${MIN_MCAP_USD} (too risky)"
    if mcap > MAX_MCAP_USD:
        return False, f"mcap ${mcap:.0f} > ${MAX_MCAP_USD} (already pumped)"

    # --- Filtres de qualité ---
    if liquidity < MIN_LIQUIDITY_USD:
        return False, f"liquidity ${liquidity:.0f} < ${MIN_LIQUIDITY_USD}"

    if age_hours is None:
        return False, "age unknown"
    if age_hours < MIN_AGE_HOURS:
        return False, f"too young ({age_hours:.1f}h)"
    if age_hours > MAX_AGE_HOURS:
        return False, f"too old ({age_hours:.1f}h)"

    if holders < MIN_HOLDERS:
        return False, f"holders {holders} < {MIN_HOLDERS}"

    if top10 is not None and top10 > MAX_TOP10_PCT:
        return False, f"top10 {top10:.1f}% > {MAX_TOP10_PCT}%"

    if risk is None:
        return False, "no risk score"
    if risk > MAX_RISK_SCORE:
        return False, f"risk {risk} > {MAX_RISK_SCORE}"

    if analysis.get("is_honeypot") is True:
        return False, "honeypot detected"

    return True, ""


def calculate_signal(analysis: dict[str, Any]) -> str:
    """Returns 'BUY', 'WATCH', or 'AVOID'."""
    risk = (analysis.get("risk") or {}).get("score") or 100
    liquidity = analysis.get("liquidity_usd") or 0
    mcap = analysis.get("market_cap_usd") or 0
    top10 = analysis.get("top10_holder_pct")
    change_h1 = analysis.get("price_change_h1") or 0

    if risk > 55:
        return "AVOID"
    if analysis.get("is_honeypot") is True:
        return "AVOID"
    if top10 is not None and top10 > 70:
        return "AVOID"
    if change_h1 > 50:
        return "AVOID"

    # BUY : score très bas + liquidité solide + holders bien répartis
    # + pas encore pumpé + mcap dans la zone basse
    if (
        risk <= 25
        and liquidity >= 50_000
        and mcap <= 120_000
        and (top10 is None or top10 < 40)
        and change_h1 < 20
    ):
        return "BUY"

    return "WATCH"
