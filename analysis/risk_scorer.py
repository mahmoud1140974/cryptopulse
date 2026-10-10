"""Transparent token risk scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(slots=True)
class RiskResult:
    score: int
    band: str
    emoji: str
    reasons: list[Any] = field(default_factory=list)

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

    # -----------------------------------------------------------------------
    # Extraction normalisée des champs
    # -----------------------------------------------------------------------
    liquidity = _float(_first(data, (
        "liquidity_usd", "liquidity", "liquidityUsd",
        "total_liquidity_usd", "value_locked_usd",
    )))

    volume = _float(_first(data, (
        "volume_24h_usd", "volume24h_usd", "volume_usd",
        "volume_24h", "volume",
    )))

    market_cap = _float(_first(data, (
        "market_cap_usd", "marketCap", "market_cap", "fdv_usd", "fdv",
    )))

    age_days = _float(_first(data, (
        "token_age_days", "age_days", "token_age",
        "age", "days_since_creation", "created_days",
    )))

    top10 = _pct(_first(data, (
        "top10_holder_pct", "top10_holders_pct",
        "top_10_holder_pct", "top_10_holders_pct",
        "top10_holders_percentage",
    )))

    # --- Champs EVM uniquement ---
    verified = _bool(_first(data, (
        "contract_verified", "verified", "is_verified", "source_verified",
    ))) if not is_solana else None

    ownership_renounced = _bool(_first(data, (
        "is_renounced", "is_owner_renounced", "ownership_renounced",
        "owner_renounced", "renounced_ownership", "renounced",
    ))) if not is_solana else None

    has_mint = _bool(_first(data, (
        "has_mint", "mintable", "is_mintable", "can_mint", "has_mint_function",
    ))) if not is_solana else None

    has_blacklist = _bool(_first(data, (
        "has_blacklist", "blacklistable", "is_blacklisted",
        "can_blacklist", "has_blacklist_function",
    ))) if not is_solana else None

    is_honeypot = _bool(_first(data, (
        "is_honeypot", "honeypot", "honeypot_detected",
    ))) if not is_solana else None

    is_proxy = _bool(_first(data, (
        "is_proxy", "is_proxy_contract", "proxy",
        "upgradeable", "is_upgradeable",
    ))) if not is_solana else None

    # --- Champs Solana uniquement ---
    freeze_authority_active = _bool(_first(data, (
        "freeze_authority_active", "freeze_authority", "freezable",
    ))) if is_solana else None

    # --- Champs communs ---
    buy_tax = _tax_pct(_first(data, (
        "buy_tax_pct", "buy_tax", "tax_buy_pct",
        "buyTax", "buy_tax_percent", "buy_fee",
    )))

    sell_tax = _tax_pct(_first(data, (
        "sell_tax_pct", "sell_tax", "tax_sell_pct",
        "sellTax", "sell_tax_percent", "sell_fee",
    )))

    has_any_data = any(
        value is not None
        for value in (
            liquidity, volume, market_cap, age_days, top10,
            verified, ownership_renounced, has_mint, has_blacklist,
            is_honeypot, is_proxy, freeze_authority_active,
            buy_tax, sell_tax,
        )
    )

    if not has_any_data:
        return RiskResult(
            score=0,
            band=INSUFFICIENT_DATA,
            emoji="⚠️",
            reasons=[{"key": "reason_insufficient_data", "params": {}}],
        )

    score = 0
    reasons: list[dict[str, Any]] = []
    missing: list[str] = []

    def _reason(key: str, **params: Any) -> None:
        """Ajoute une raison sous forme structurée (clé de traduction + paramètres)."""
        reasons.append({"key": key, "params": params})

    # --- Liquidité ---
    if liquidity is None:
        missing.append("liquidity")
    elif liquidity < 10_000:
        score += 18
        _reason("reason_liquidity_very_low", value=_money(liquidity))
    elif liquidity < 50_000:
        score += 10
        _reason("reason_liquidity_low", value=_money(liquidity))
    elif liquidity < 250_000:
        score += 4
        _reason("reason_liquidity_modest", value=_money(liquidity))

    # --- Volume 24h ---
    if volume is None:
        missing.append("24h volume")
    elif volume < 1_000:
        score += 8
        _reason("reason_volume_very_low", value=_money(volume))
    elif volume < 10_000:
        score += 4
        _reason("reason_volume_low", value=_money(volume))

    # --- Market cap ---
    if market_cap is None:
        missing.append("market cap")
    elif market_cap < 100_000:
        score += 8
        _reason("reason_mcap_very_small", value=_money(market_cap))
    elif market_cap < 1_000_000:
        score += 4
        _reason("reason_mcap_small", value=_money(market_cap))

    # --- Âge du token ---
    if age_days is None:
        missing.append("token age")
    elif age_days < 1:
        score += 12
        _reason("reason_age_less_than_day")
    elif age_days < 7:
        score += 8
        _reason("reason_age_days", days=max(int(age_days), 0))
    elif age_days < 30:
        score += 4
        _reason("reason_age_young", days=int(age_days))

    # --- Concentration holders ---
    if top10 is None:
        missing.append("top 10 holder %")
    elif top10 > 80:
        score += 25
        _reason("reason_top10_control", pct=f"{top10:.2f}")
    elif top10 > 50:
        score += 18
        _reason("reason_top10_control", pct=f"{top10:.2f}")
    elif top10 > 30:
        score += 8
        _reason("reason_top10_control", pct=f"{top10:.2f}")

    # --- Champs EVM uniquement (contrat, honeypot, proxy, etc.) ---
    if not is_solana:
        if verified is None:
            missing.append("contract verification")
        elif verified is False:
            score += 10
            _reason("reason_contract_unverified")

        if ownership_renounced is None:
            missing.append("ownership renouncement")
        elif ownership_renounced is False:
            score += 8
            _reason("reason_ownership_not_renounced")

        if has_mint is None:
            missing.append("mint function")
        elif has_mint is True:
            score += 15
            _reason("reason_mint_function")

        if has_blacklist is None:
            missing.append("blacklist function")
        elif has_blacklist is True:
            score += 10
            _reason("reason_blacklist_function")

        if is_honeypot is None:
            missing.append("honeypot check")
        elif is_honeypot is True:
            score += 50
            _reason("reason_honeypot_detected")

        if is_proxy is None:
            missing.append("proxy/upgradeable check")
        elif is_proxy is True:
            score += 8
            _reason("reason_proxy_contract")

    # --- Freeze authority (Solana uniquement) ---
    if is_solana:
        if freeze_authority_active is None:
            missing.append("freeze authority")
        elif freeze_authority_active is True:
            score += 20
            _reason("reason_freeze_authority")

    # --- Buy/sell tax (commun, souvent absent sur Solana) ---
    if buy_tax is None and sell_tax is None:
        missing.append("buy/sell tax")
    else:
        if buy_tax is None:
            missing.append("buy tax")
        if sell_tax is None:
            missing.append("sell tax")

        high_buy = buy_tax is not None and buy_tax > 10
        high_sell = sell_tax is not None and sell_tax > 10

        if high_buy or high_sell:
            if (buy_tax is not None and buy_tax > 20) or (
                sell_tax is not None and sell_tax > 20
            ):
                score += 18
            else:
                score += 12
            if high_buy and high_sell:
                _reason(
                    "reason_high_tax_both",
                    buy=f"{buy_tax:.2f}%",
                    sell=f"{sell_tax:.2f}%",
                )
            elif high_buy:
                _reason("reason_high_tax_buy", value=f"{buy_tax:.2f}%")
            else:
                _reason("reason_high_tax_sell", value=f"{sell_tax:.2f}%")

    # --- Data completeness guardrail ---
    market_known = any(
        value is not None for value in (liquidity, volume, market_cap, age_days)
    )
    holder_known = top10 is not None

    if is_solana:
        # Sur Solana, la seule donnée de "security" est freeze_authority_active.
        security_known = freeze_authority_active is not None
    else:
        security_known = any(
            value is not None
            for value in (
                verified, ownership_renounced, has_mint, has_blacklist,
                is_honeypot, is_proxy, buy_tax, sell_tax,
            )
        )

    categories_known = sum(
        1 for flag in (market_known, holder_known, security_known) if flag
    )

    if categories_known == 1:
        score += 25
        _reason("reason_one_category")
    elif categories_known == 2:
        if not security_known:
            score += 12
            _reason("reason_no_security_data")
        elif not holder_known:
            score += 5
            _reason("reason_no_holder_data")
        elif not market_known:
            score += 5
            _reason("reason_no_market_data")

    # --- Unknown factors ---
    if missing:
        missing_unique = list(dict.fromkeys(missing))
        _reason("reason_unknown_fields", fields=", ".join(missing_unique))

    if score == 0:
        reasons.insert(0, {"key": "reason_no_risk_flags", "params": {}})

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


_PLACEHOLDER_VALUES = {
    "", "-", "--", "n/a", "na", "unknown", "null", "none", "undefined", "nan",
}


def _first(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
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
