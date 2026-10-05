"""Provider and address validation tests."""

from __future__ import annotations

from providers.base import ProviderError
from providers.dexscreener import DexScreenerProvider
from providers.fallback_manager import FallbackManager
from utils.validators import validate_address


def test_evm_address_validation() -> None:
    result = validate_address("0x" + "a" * 40)
    assert result.is_valid is True
    assert result.chain == "evm"


def test_solana_address_validation() -> None:
    result = validate_address("So11111111111111111111111111111111111111112")
    assert result.is_valid is True
    assert result.chain == "solana"


def test_invalid_address_validation() -> None:
    result = validate_address("not-an-address")
    assert result.is_valid is False
    assert result.reason


async def test_fallback_manager_uses_second_provider() -> None:
    async def fails():
        raise ProviderError("provider A down")

    async def works():
        return {"price_usd": 1.23}

    result = await FallbackManager().first_success([
        ("provider_a", fails),
        ("provider_b", works),
    ])

    assert result.provider == "provider_b"
    assert result.data["price_usd"] == 1.23
    assert result.errors


class FakeDexScreener(DexScreenerProvider):
    async def _get_json(self, url: str, params=None, headers=None):
        return {
            "pairs": [
                {
                    "chainId": "ethereum",
                    "dexId": "uniswap",
                    "priceUsd": "0.5",
                    "marketCap": "1000000",
                    "pairCreatedAt": 1_700_000_000_000,
                    "baseToken": {"address": "0x" + "a" * 40, "name": "Test Token", "symbol": "TEST"},
                    "quoteToken": {"symbol": "WETH"},
                    "liquidity": {"usd": "25000"},
                    "volume": {"h24": "5000"},
                    "txns": {"h24": {"buys": 12, "sells": 3}},
                }
            ]
        }


async def test_dexscreener_snapshot_parsing() -> None:
    provider = FakeDexScreener()
    snapshot = await provider.get_token_snapshot("0x" + "a" * 40)
    assert snapshot["chain"] == "ethereum"
    assert snapshot["symbol"] == "TEST"
    assert snapshot["price_usd"] == 0.5
    assert snapshot["liquidity_usd"] == 25000
    assert snapshot["volume_24h_usd"] == 5000
    assert snapshot["buys_24h"] == 12
