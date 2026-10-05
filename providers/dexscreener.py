"""DexScreener provider for DEX pairs, liquidity, price, and activity."""

from __future__ import annotations

import logging
from typing import Any

from cachetools import TTLCache

from .base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


class DexScreenerProvider(BaseProvider):
    name = "dexscreener"
    base_url = "https://api.dexscreener.com/latest/dex"
    root_url = "https://api.dexscreener.com"

    def __init__(self, timeout: float = 10.0, max_retries: int = 3) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries)
        self._cache: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=500, ttl=60)

    async def get_token_snapshot(self, address: str) -> dict[str, Any]:
        cache_key = address.lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        data = await self._get_json(f"{self.base_url}/tokens/{address}")
        pairs = data.get("pairs") or []
        if not pairs:
            logger.warning("dexscreener returned no pairs for address %s", address)
            raise ProviderError("DexScreener returned no pairs for this token")

        primary = max(pairs, key=lambda pair: _float(pair.get("liquidity", {}).get("usd")) or 0)
        base_token = primary.get("baseToken") or {}
        quote_token = primary.get("quoteToken") or {}
        token = base_token if str(base_token.get("address", "")).lower() == address.lower() else base_token
        txns = primary.get("txns", {}).get("h24", {}) or {}

        snapshot = {
            "provider": self.name,
            "address": address,
            "chain": primary.get("chainId"),
            "dex": primary.get("dexId"),
            "name": token.get("name"),
            "symbol": token.get("symbol"),
            "price_usd": _float(primary.get("priceUsd")),
            "liquidity_usd": sum(_float((pair.get("liquidity") or {}).get("usd")) or 0 for pair in pairs),
            "volume_24h_usd": sum(_float((pair.get("volume") or {}).get("h24")) or 0 for pair in pairs),
            "market_cap_usd": _float(primary.get("marketCap")) or _float(primary.get("fdv")),
            "pair_created_at": primary.get("pairCreatedAt"),
            "buys_24h": _int(txns.get("buys")),
            "sells_24h": _int(txns.get("sells")),
            "quote_symbol": quote_token.get("symbol"),
            "pairs_count": len(pairs),
        }
        self._cache[cache_key] = snapshot
        return snapshot

    async def get_trending(self, chain: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Return latest boosted tokens as a free trending approximation."""
        data = await self._get_json(f"{self.root_url}/token-boosts/latest/v1")
        items = data if isinstance(data, list) else data.get("tokens", [])
        results = []
        for item in items:
            if chain and item.get("chainId") != chain:
                continue
            results.append(item)
            if len(results) >= limit:
                break
        return results


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
