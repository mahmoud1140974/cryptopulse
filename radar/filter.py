"""Radar filter — applies quality criteria to new tokens."""

from __future__ import annotations

import time
from typing import Any

MIN_LIQUIDITY_USD = 30_000
MIN_AGE_HOURS = 2
MAX_AGE_HOURS = 48
MIN_HOLDERS = 100
MAX_TOP10_PCT = 60
MAX_RISK_SCORE = 40


def calculate_age_hours(pair_created_at_ms: int | None) -> float | None:
    if not pair_created_at_ms:
        return None
    return max((time.time() * 1000 - pair_created_at_ms) / 3_600_000, 0)


def apply_filters(analysis: dict[str, Any]) -> tuple[bool, str]:
    """
    Returns (passed: bool, reason: str).
    If passed=True, reason is empty.
    """
    liquidity = analysis.get("liquidity_usd") or 0
    holders = analysis.get("holder_count") or 0
    top10 = analysis.get("top10_holder_pct")
    risk = (analysis.get("risk") or {}).get("score")
    age_hours = calculate_age_hours(analysis.get("pair_created_at"))

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
    top10 = analysis.get("top10_holder_pct")

    if risk > 55:
        return "AVOID"
    if analysis.get("is_honeypot") is True:
        return "AVOID"
    if top10 is not None and top10 > 70:
        return "AVOID"

    if risk <= 25 and liquidity >= 50_000 and (top10 is None or top10 < 40):
        return "BUY"

    return "WATCH"
