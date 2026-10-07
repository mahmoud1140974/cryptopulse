"""Transparent token risk scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ---------------------------------------------------------------------------
# Points model (higher score = higher risk). Final score is capped at 0..100.
#
# Market / liquidity
#   liquidity < $10k       +18
#   liquidity < $50k       +10
#   liquidity < $250k      +4
#   volume < $1k           +8
#   volume < $10k          +4
#   market cap < $100k     +8
#   market cap < $1M       +4
#
# Token age
#   age < 1 day            +12
#   age < 7 days           +8
#   age < 30 days          +4
#
# Holder concentration
#   top10 > 80%            +25
#   top10 > 50%            +18
#   top10 > 30%            +8
#
# Contract / security
#   honeypot               +50
#   freeze authority       +20  (Solana uniquement)
#   mint function          +15
#   blacklist function     +10
#   unverified contract    +10
#   ownership active       +8
#   proxy/upgradeable      +8
#   tax > 20%              +18
#   tax > 10%              +12
#
# Data completeness guardrails
#   only one data category available       +25
#   two categories, no security data       +12
#   two categories, missing holder/market  +5
#
# Missing fields are listed as "Unknown: ..." in reasons.
# If no risk-relevant fields exist, the result band is INSUFFICIENT_DATA.
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class RiskResult:
    score: int
    band: str
    emoji: str
    reasons: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return INSUFFICIENT_DATA if self.band == INSUFFICIENT_DATA else "OK"

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "band": self.band,
            "emoji": self.emoji,
            "reasons": self.reasons,
        }


def score_token(data: dict[str, Any]) -> RiskResult:
    if not isinstance(data, dict):
        data = {}

    chain = str(_first(data, ("chain", "blockchain", "network")) or "").strip().lower()
    is_solana = chain == "solana"

    liquidity = _float(
        _first(
            data,
            (
                "liquidity_usd",
                "liquidity",
                "liquidityUsd",
                "total_liquidity_usd",
                "value_locked_usd",
            ),
        )
    )

    volume = _float(
        _first(
            data,
            (
                "volume_24h_usd",
                "volume24h_usd",
                "volume_usd",
                "volume_24h",
                "volume",
            ),
        )
    )

    market_cap = _float(
        _first(
            data,
            (
                "market_cap_usd",
                "marketCap",
                "market_cap",
                "fdv_usd",
                "fdv",
            ),
        )
    )

    age_days = _float(
        _first(
            data,
            (
                "token_age_days",
                "age_days",
                "token_age",
                "age",
                "days_since_creation",
                "created_days",
            ),
        )
    )

    top10 = _pct(
        _first(
            data,
            (
                "top10_holder_pct",
                "top10_holders_pct",
                "top_10_holder_pct",
                "top_10_holders_pct",
                "top10_holders_percentage",
            ),
        )
    )

    verified = _bool(
        _first(
            data,
            (
                "contract_verified",
                "verified",
                "is_verified",
                "source_verified",
            ),
        )
    )

    # Ownership : on essaie is_renounced EN PREMIER car c'est le nom
    # utilisé par GoPlus et par le formatter.
    ownership_renounced = _bool(
        _first(
            data,
            (
                "is_renounced",
                "is_owner_renounced",
                "ownership_renounced",
                "owner_renounced",
                "renounced_ownership",
                "renounced",
            ),
        )
    )

    has_mint = _bool(
        _first(
            data,
            (
                "has_mint",
                "mintable",
                "is_mintable",
                "can_mint",
                "has_mint_function",
            ),
        )
    )

    has_blacklist = _bool(
        _first(
            data,
            (
                "has_blacklist",
                "blacklistable",
                "is_blacklisted",
                "can_blacklist",
                "has_blacklist_function",
            ),
        )
    )

    is_honeypot = _bool(
        _first(
            data,
            (
                "is_honeypot",
                "honeypot",
                "honeypot_detected",
            ),
        )
    )

    is_proxy = _bool(
        _first(
            data,
            (
                "is_proxy",
                "is_proxy_contract",
                "proxy",
                "upgradeable",
                "is_upgradeable",
            ),
        )
    )

    freeze_authority_active = _bool(
        _first(
            data,
            (
                "freeze_authority_active",
                "freeze_authority",
                "freezable",
            ),
        )
    )

    buy_tax = _tax_pct(
        _first(
            data,
            (
                "buy_tax_pct",
                "buy_tax",
                "tax_buy_pct",
                "buyTax",
                "buy_tax_percent",
                "buy_fee",
            ),
        )
    )

    sell_tax = _tax_pct(
        _first(
            data,
            (
                "sell_tax_pct",
                "sell_tax",
                "tax_sell_pct",
                "sellTax",
                "sell_tax_percent",
                "sell_fee",
            ),
        )
    )

    has_any_data = any(
        value is not None
        for value in (
            liquidity,
            volume,
            market_cap,
            age_days,
            top10,
            verified,
            ownership_renounced,
            has_mint,
            has_blacklist,
            is_honeypot,
            is_proxy,
            freeze_authority_active if is_solana else None,
            buy_tax,
            sell_tax,
        )
    )

    if not has_any_data:
        return RiskResult(
            score=0,
            band=INSUFFICIENT_DATA,
            emoji="⚠️",
            reasons=["Insufficient data to assess risk"],
        )

    score = 0
    reasons: list[str] = []
    missing: list[str] = []

    # --- Liquidité ---
    if liquidity is None:
        missing.append("liquidity")
    elif liquidity < 10_000:
        score += 18
        reasons.append(f"Liquidity is very low ({_money(liquidity)})")
    elif liquidity < 50_000:
        score += 10
        reasons.append(f"Liquidity is low ({_money(liquidity)})")
    elif liquidity < 250_000:
        score += 4
        reasons.append(f"Liquidity is modest ({_money(liquidity)})")

    # --- Volume 24h ---
    if volume is None:
        missing.append("24h volume")
    elif volume < 1_000:
        score += 8
        reasons.append(f"24h volume is very low ({_money(volume)})")
    elif volume < 10_000:
        score += 4
        reasons.append(f"24h volume is low ({_money(volume)})")

    # --- Market cap ---
    if market_cap is None:
        missing.append("market cap")
    elif market_cap < 100_000:
        score += 8
        reasons.append(f"Market cap is very small ({_money(market_cap)})")
    elif market_cap < 1_000_000:
        score += 4
        reasons.append(f"Market cap is small ({_money(market_cap)})")

    # --- Âge du token ---
    if age_days is None:
        missing.append("token age")
    elif age_days < 1:
        score += 12
        reasons.append("Token is less than 1 day old")
    elif age_days < 7:
        score += 8
        reasons.append(f"Token created {max(int(age_days), 0)} day(s) ago")
    elif age_days < 30:
        score += 4
        reasons.append(f"Token is young ({int(age_days)} day(s) old)")

    # --- Concentration holders ---
    if top10 is None:
        missing.append("top 10 holder %")
    elif top10 > 80:
        score += 25
        reasons.append(f"Top 10 holders control {top10:.2f}% of supply")
    elif top10 > 50:
        score += 18
        reasons.append(f"Top 10 holders control {top10:.2f}% of supply")
    elif top10 > 30:
        score += 8
        reasons.append(f"Top 10 holders control {top10:.2f}% of supply")

    # --- Vérification du contrat ---
    if verified is None:
        missing.append("contract verification")
    elif verified is False:
        score += 10
        reasons.append("Contract source is not verified")

    # --- Ownership ---
    if ownership_renounced is None:
        missing.append("ownership renouncement")
    elif ownership_renounced is False:
        score += 8
        reasons.append("Contract ownership has not been renounced")

    # --- Mint function ---
    if has_mint is None:
        missing.append("mint function")
    elif has_mint is True:
        score += 15
        reasons.append("Mint function detected in contract")

    # --- Blacklist function ---
    if has_blacklist is None:
        missing.append("blacklist function")
    elif has_blacklist is True:
        score += 10
        reasons.append("Blacklist function detected in contract")

    # --- Honeypot ---
    if is_honeypot is None:
        missing.append("honeypot check")
    elif is_honeypot is True:
        score += 50
        reasons.append("Honeypot detected")

    # --- Proxy / upgradeable ---
    if is_proxy is None:
        missing.append("proxy/upgradeable check")
    elif is_proxy is True:
        score += 8
        reasons.append("Proxy or upgradeable contract detected")

    # --- Freeze authority (Solana uniquement) ---
    if is_solana:
        if freeze_authority_active is None:
            missing.append("freeze authority")
        elif freeze_authority_active is True:
            score += 20
            reasons.append("Solana freeze authority is active")

    # --- Buy/sell tax ---
    if buy_tax is None and sell_tax is None:
        missing.append("buy/sell tax")
    else:
        if buy_tax is None:
            missing.append("buy tax")
        if sell_tax is None:
            missing.append("sell tax")

        tax_bits: list[str] = []
        if buy_tax is not None and buy_tax > 10:
            tax_bits.append(f"buy tax {buy_tax:.2f}%")
        if sell_tax is not None and sell_tax > 10:
            tax_bits.append(f"sell tax {sell_tax:.2f}%")

        if tax_bits:
            if (buy_tax is not None and buy_tax > 20) or (
                sell_tax is not None and sell_tax > 20
            ):
                score += 18
            else:
                score += 12

            reasons.append("High token tax detected (" + ", ".join(tax_bits) + ")")

    # --- Data completeness guardrail ---
    market_known = any(
        value is not None for value in (liquidity, volume, market_cap, age_days)
    )
    holder_known = top10 is not None
    security_known = any(
        value is not None
        for value in (
            verified,
            ownership_renounced,
            has_mint,
            has_blacklist,
            is_honeypot,
            is_proxy,
            freeze_authority_active if is_solana else None,
            buy_tax,
            sell_tax,
        )
    )

    categories_known = sum(
        1 for flag in (market_known, holder_known, security_known) if flag
    )

    if categories_known == 1:
        score += 25
        reasons.append("Only one data category is available; risk may be underestimated")
    elif categories_known == 2:
        if not security_known:
            score += 12
            reasons.append("No security data available; risk may be underestimated")
        elif not holder_known:
            score += 5
            reasons.append("No holder concentration data available")
        elif not market_known:
            score += 5
            reasons.append("No market data available")

    # --- Unknown factors ---
    if missing:
        missing_unique = list(dict.fromkeys(missing))
        reasons.append("Unknown: " + ", ".join(missing_unique))

    if score == 0:
        reasons.insert(0, "No risk flags found in available data")

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


# Valeurs textuelles considérées comme "pas de donnée" même si ce ne sont pas des None
_PLACEHOLDER_VALUES = {
    "", "-", "--", "n/a", "na", "unknown", "null", "none", "undefined", "nan",
}


def _first(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """
    Retourne la première valeur UTILE trouvée parmi les clés données.

    Ignore :
      - les valeurs None
      - les chaînes vides
      - les placeholders textuels ("unknown", "n/a", "-", ...)

    Les valeurs False et 0 restent considérées comme valides (importantes).
    """
    for key in keys:
        if key not in data:
            continue
        value = data[key]
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip().lower()
            if stripped in _PLACEHOLDER_VALUES:
                continue
        return value
    return None


def _float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace("$", "").replace(",", "")
        if not cleaned or cleaned.lower() in {"none", "null", "n/a", "na", "unknown"}:
            return None
        value = cleaned
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pct(value: Any) -> float | None:
    result = _float(value)
    if result is None:
        return None
    if result < 0:
        return None
    return min(result, 100.0)


def _tax_pct(value: Any) -> float | None:
    """
    Normalise une taxe en pourcentage.

    GoPlus renvoie souvent un décimal (0.05 = 5%). Certains providers renvoient
    déjà un pourcentage (5 = 5%). On gère les deux cas.
    """
    result = _float(value)
    if result is None:
        return None
    if result < 0:
        return None
    if result <= 1:
        result = result * 100
    return min(result, 100.0)


def _bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {
            "true", "yes", "y", "1",
            "verified", "active", "enabled", "renounced",
        }:
            return True
        if normalized in {
            "false", "no", "n", "0",
            "unverified", "inactive", "disabled",
            "not_renounced", "ownership_active",
        }:
            return False
    return None


def _money(value: float) -> str:
    return f"${value:,.2f}"
