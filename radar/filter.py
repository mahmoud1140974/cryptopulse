"""Radar filter — applies quality criteria to new tokens."""

from __future__ import annotations

import time
from typing import Any

# --- Filtres de base (EVM) ---
MIN_LIQUIDITY_USD = 30_000
MIN_AGE_HOURS = 1.0
MAX_AGE_HOURS = 6.0
MIN_HOLDERS = 100
MAX_TOP10_PCT = 60
MAX_RISK_SCORE = 40

# --- Filtre MARKET CAP ---
MIN_MCAP_USD = 5_000   # On exige 5k$ minimum
MAX_MCAP_USD = 200_000

# --- Filtres ANTI-PUMP ---
MAX_PRICE_CHANGE_H1 = 50.0
MAX_PRICE_CHANGE_H6 = 100.0
MAX_PRICE_CHANGE_H24 = 200.0

# --- Filtre Spécial Solana / Pump.fun ---
SOLANA_MIN_AGE_HOURS = 0.25  # On exige 15 minutes d'âge minimum sur Solana


def calculate_age_hours(pair_created_at_ms: int | None) -> float | None:
    if not pair_created_at_ms:
        return None
    try:
        if pair_created_at_ms < 10_000_000_000:
            pair_created_at_ms = pair_created_at_ms * 1000
        return max((time.time() * 1000 - pair_created_at_ms) / 3_600_000, 0)
    except Exception:
        return None


def apply_filters(analysis: dict[str, Any]) -> tuple[bool, str]:
    liquidity = analysis.get("liquidity_usd") or 0
    mcap = analysis.get("market_cap_usd")
    holders = analysis.get("holder_count") or 0
    top10 = analysis.get("top10_holder_pct")
    risk = (analysis.get("risk") or {}).get("score")
    age_hours = calculate_age_hours(analysis.get("pair_created_at"))

    # --- Anti-pump ---
    change_h1 = analysis.get("price_change_h1")
    change_h6 = analysis.get("price_change_h6")
    change_h24 = analysis.get("price_change_h24")

    if change_h1 is not None and change_h1 > MAX_PRICE_CHANGE_H1:
        return False, f"already pumped +{change_h1:.0f}% in 1h"
    if change_h6 is not None and change_h6 > MAX_PRICE_CHANGE_H6:
        return False, f"already pumped +{change_h6:.0f}% in 6h"
    if change_h24 is not None and change_h24 > MAX_PRICE_CHANGE_H24:
        return False, f"already pumped +{change_h24:.0f}% in 24h"

    # --- RÈGLE SPÉCIALE SOLANA (Stricte) ---
    if analysis.get("chain") == "solana" or analysis.get("source") == "pumpfun":
        # 1. Vérification Market Cap (Si inconnu, on rejette)
        if mcap is None:
            return False, "mcap unknown"
        if mcap > MAX_MCAP_USD:
            return False, f"mcap too high (${mcap:.0f})"
        if mcap < MIN_MCAP_USD:
            return False, f"mcap too low (${mcap:.0f})"
        
        # 2. Vérification Âge (Si inconnu, on rejette)
        if age_hours is None:
            return False, "age unknown"
        if age_hours < SOLANA_MIN_AGE_HOURS:
            return False, f"too young ({age_hours * 60:.0f} min)"
            
        return True, ""

    # --- Filtres EVM ---
    if mcap is None:
        return False, "market cap unknown"
    if mcap < MIN_MCAP_USD:
        return False, "mcap too low"
    if mcap > MAX_MCAP_USD:
        return False, "mcap too high"
    if liquidity < MIN_LIQUIDITY_USD:
        return False, "low liquidity"
    if age_hours is None or age_hours < MIN_AGE_HOURS:
        return False, "too young"
    if age_hours > MAX_AGE_HOURS:
        return False, "too old"
    if holders < MIN_HOLDERS:
        return False, "not enough holders"
    if top10 is not None and top10 > MAX_TOP10_PCT:
        return False, "top10 too high"
    if risk is not None and risk > MAX_RISK_SCORE:
        return False, "risk too high"
    if analysis.get("is_honeypot") is True:
        return False, "honeypot detected"

    return True, ""


def calculate_signal(analysis: dict[str, Any]) -> str:
    if analysis.get("chain") == "solana" or analysis.get("source") == "pumpfun":
        return "WATCH" 

    risk = (analysis.get("risk") or {}).get("score") or 100
    liquidity = analysis.get("liquidity_usd") or 0
    mcap = analysis.get("market_cap_usd") or 0
    top10 = analysis.get("top10_holder_pct")
    change_h1 = analysis.get("price_change_h1") or 0

    if risk > 55 or analysis.get("is_honeypot") or (top10 and top10 > 70) or change_h1 > 50:
        return "AVOID"

    if risk <= 25 and liquidity >= 50_000 and mcap <= 120_000 and (top10 is None or top10 < 40) and change_h1 < 20:
        return "BUY"

    return "WATCH"
