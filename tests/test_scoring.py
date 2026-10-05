"""Risk scoring tests with known inputs."""

from __future__ import annotations

from analysis.risk_scorer import score_token


def test_low_risk_score() -> None:
    result = score_token(
        {
            "liquidity_usd": 100_000,
            "top10_holder_pct": 20,
            "contract_verified": True,
            "has_mint": False,
            "has_blacklist": False,
            "ownership_renounced": True,
            "token_age_days": 30,
            "volume_24h_usd": 50_000,
            "buy_tax_pct": 0,
            "sell_tax_pct": 0,
            "is_honeypot": False,
            "is_proxy": False,
            "freeze_authority_active": False,
        }
    )
    assert result.score == 0
    assert result.band == "LOW RISK"
    assert result.emoji == "🟢"


def test_medium_risk_score() -> None:
    result = score_token({"liquidity_usd": 5_000, "contract_verified": False})
    assert result.score == 25
    assert result.band == "MEDIUM RISK"
    assert any("Liquidity" in reason for reason in result.reasons)
    assert any("not verified" in reason for reason in result.reasons)


def test_extreme_risk_score_is_capped() -> None:
    result = score_token(
        {
            "liquidity_usd": 1_000,
            "top10_holder_pct": 90,
            "contract_verified": False,
            "has_mint": True,
            "has_blacklist": True,
            "ownership_renounced": False,
            "token_age_days": 1,
            "volume_24h_usd": 100,
            "buy_tax_pct": 15,
            "sell_tax_pct": 15,
            "is_honeypot": True,
            "is_proxy": True,
            "freeze_authority_active": True,
        }
    )
    assert result.score == 100
    assert result.band == "EXTREME RISK"
    assert result.emoji == "🔴"


def test_missing_data_does_not_create_fake_reasons() -> None:
    result = score_token({})
    assert result.score == 0
    assert result.reasons == []
