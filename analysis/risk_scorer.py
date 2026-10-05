"""Transparent token risk scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RiskResult:
    score: int
    band: str
    emoji: str
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"score": self.score, "band": self.band, "emoji": self.emoji, "reasons": self.reasons}


def score_token(data: dict[str, Any]) -> RiskResult:
    score = 0
    reasons: list[str] = []

    liquidity = _float(data.get("liquidity_usd"))
    if liquidity is not None and liquidity < 10_000:
        score += 15
        reasons.append(f"Liquidity is low ({_money(liquidity)})")

    top10 = _float(data.get("top10_holder_pct"))
    if top10 is not None and top10 > 50:
        score += 20
        reasons.append(f"Top 10 holders control {top10:.2f}% of supply")

    verified = data.get("contract_verified")
    if verified is False:
        score += 10
        reasons.append("Contract source is not verified")

    if data.get("has_mint") is True:
        score += 15
        reasons.append("Mint function detected in contract")

    if data.get("has_blacklist") is True:
        score += 10
        reasons.append("Blacklist function detected in contract")

    ownership_renounced = data.get("ownership_renounced")
    if ownership_renounced is False:
        score += 10
        reasons.append("Contract ownership is still active")

    age_days = _float(data.get("token_age_days"))
    if age_days is not None and age_days < 7:
        score += 8
        reasons.append(f"Token created {max(int(age_days), 0)} day(s) ago")

    volume = _float(data.get("volume_24h_usd"))
    if volume is not None and volume < 1_000:
        score += 7
        reasons.append(f"24h volume is low ({_money(volume)})")

    buy_tax = _float(data.get("buy_tax_pct"))
    sell_tax = _float(data.get("sell_tax_pct"))
    if (buy_tax is not None and buy_tax > 10) or (sell_tax is not None and sell_tax > 10):
        score += 10
        tax_bits = []
        if buy_tax is not None:
            tax_bits.append(f"buy tax {buy_tax:.2f}%")
        if sell_tax is not None:
            tax_bits.append(f"sell tax {sell_tax:.2f}%")
        reasons.append("High token tax detected (" + ", ".join(tax_bits) + ")")

    if data.get("is_honeypot") is True:
        score += 25
        reasons.append("Honeypot detected")

    if data.get("is_proxy") is True:
        score += 8
        reasons.append("Proxy or upgradeable contract detected")

    if data.get("freeze_authority_active") is True:
        score += 15
        reasons.append("Solana freeze authority is active")

    score = max(0, min(score, 100))
    band, emoji = _band(score)
    return RiskResult(score=score, band=band, emoji=emoji, reasons=reasons)


def _band(score: int) -> tuple[str, str]:
    if score <= 20:
        return "LOW RISK", "🟢"
    if score <= 45:
        return "MEDIUM RISK", "🟡"
    if score <= 70:
        return "HIGH RISK", "🟠"
    return "EXTREME RISK", "🔴"


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _money(value: float) -> str:
    return f"${value:,.2f}"
