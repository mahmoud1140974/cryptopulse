"""CoinGecko provider for market metadata and price fallback."""

from __future__ import annotations

import logging
from typing import Any

from cachetools import TTLCache

from .base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


CHAIN_TO_PLATFORM = {
    "ethereum": "ethereum",
    "bsc": "binance-smart-chain",
    "polygon": "polygon-pos",
    "arbitrum": "arbitrum-one",
    "base": "base",
}


class CoinGeckoProvider(BaseProvider):
    name = "coingecko"
    base_url = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key: str | None = None, timeout: float = 10.0, max_retries: int = 3) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries)
        self.api_key = api_key
        self._cache: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=500, ttl=60)

    async def get_token_snapshot(self, address: str, chain: str | None = None) -> dict[str, Any]:
        platform = CHAIN_TO_PLATFORM.get((chain or "").lower())
        if not platform:
            logger.warning("coingecko contract lookup unsupported for chain %s", chain)
            raise ProviderError("CoinGecko contract lookup requires a supported EVM chain")

        cache_key = f"{platform}:{address.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = {"x-cg-demo-api-key": self.api_key} if self.api_key else None
        data = await self._get_json(f"{self.base_url}/coins/{platform}/contract/{address}", headers=headers)
        if not data or not data.get("id"):
            logger.warning("coingecko returned no token data for %s on %s", address, platform)
            raise ProviderError("CoinGecko returned no token data")
        market = data.get("market_data") or {}
        current_price = (market.get("current_price") or {}).get("usd")
        market_cap = (market.get("market_cap") or {}).get("usd")
        volume = (market.get("total_volume") or {}).get("usd")

        snapshot = {
            "provider": self.name,
            "address": address,
            "chain": chain,
            "coingecko_id": data.get("id"),
            "name": data.get("name"),
            "symbol": (data.get("symbol") or "").upper() or None,
            "price_usd": _float(current_price),
            "liquidity_usd": None,
            "volume_24h_usd": _float(volume),
            "market_cap_usd": _float(market_cap),
            "pair_created_at": None,
            "buys_24h": None,
            "sells_24h": None,
        }
        self._cache[cache_key] = snapshot
        return snapshot

    async def get_global_market(self) -> dict[str, Any]:
        data = await self._get_json(f"{self.base_url}/global")
        return data.get("data") or {}


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
