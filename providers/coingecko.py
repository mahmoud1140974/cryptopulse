"""CoinGecko provider with robust caching to avoid rate limits."""

from __future__ import annotations

import logging
import time
from typing import Any

from .base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


CHAIN_TO_PLATFORM = {
    "ethereum": "ethereum",
    "bsc": "binance-smart-chain",
    "polygon": "polygon-pos",
    "arbitrum": "arbitrum-one",
    "base": "base",
}


class _SimpleCache:
    """
    Cache simple avec TTL + fallback sur données expirées.

    Quand une clé expire, on la garde encore en mémoire comme
    'stale' pour pouvoir la renvoyer si le fournisseur répond 429.
    """

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = ttl_seconds
        self.store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str, allow_stale: bool = False) -> Any | None:
        if key not in self.store:
            return None
        ts, value = self.store[key]
        age = time.time() - ts
        if age < self.ttl:
            return value
        if allow_stale:
            return value
        return None

    def set(self, key: str, value: Any) -> None:
        self.store[key] = (time.time(), value)


class CoinGeckoProvider(BaseProvider):
    name = "coingecko"
    base_url = "https://api.coingecko.com/api/v3"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 10.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries)
        self.api_key = api_key
        # Caches avec TTL long pour éviter les 429
        self._token_cache = _SimpleCache(ttl_seconds=3600)   # 1h pour les tokens
        self._markets_cache = _SimpleCache(ttl_seconds=300)  # 5min pour top coins
        self._global_cache = _SimpleCache(ttl_seconds=600)   # 10min pour global

    def _headers(self) -> dict[str, str] | None:
        return {"x-cg-demo-api-key": self.api_key} if self.api_key else None

    async def get_token_snapshot(self, address: str, chain: str | None = None) -> dict[str, Any]:
        platform = CHAIN_TO_PLATFORM.get((chain or "").lower())
        if not platform:
            logger.warning("coingecko contract lookup unsupported for chain %s", chain)
            raise ProviderError("CoinGecko contract lookup requires a supported EVM chain")

        cache_key = f"{platform}:{address.lower()}"
        cached = self._token_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data = await self._get_json(
                f"{self.base_url}/coins/{platform}/contract/{address}",
                headers=self._headers(),
            )
        except Exception as exc:
            stale = self._token_cache.get(cache_key, allow_stale=True)
            if stale is not None:
                logger.warning("coingecko 429 — using stale token cache")
                return stale
            raise

        if not data or not data.get("id"):
            raise ProviderError("CoinGecko returned no token data")

        market = data.get("market_data") or {}
        snapshot = {
            "provider": self.name,
            "address": address,
            "chain": chain,
            "coingecko_id": data.get("id"),
            "name": data.get("name"),
            "symbol": (data.get("symbol") or "").upper() or None,
            "price_usd": _float((market.get("current_price") or {}).get("usd")),
            "liquidity_usd": None,
            "volume_24h_usd": _float((market.get("total_volume") or {}).get("usd")),
            "market_cap_usd": _float((market.get("market_cap") or {}).get("usd")),
            "pair_created_at": None,
            "buys_24h": None,
            "sells_24h": None,
        }
        self._token_cache.set(cache_key, snapshot)
        return snapshot

    async def get_global_market(self) -> dict[str, Any]:
        cached = self._global_cache.get("global")
        if cached is not None:
            return cached

        try:
            data = await self._get_json(
                f"{self.base_url}/global",
                headers=self._headers(),
            )
        except Exception as exc:
            stale = self._global_cache.get("global", allow_stale=True)
            if stale is not None:
                logger.warning("coingecko 429 — using stale global cache")
                return stale
            raise

        result = data.get("data") or {}
        self._global_cache.set("global", result)
        return result

    async def get_top_coins(self, limit: int = 10) -> list[dict[str, Any]]:
        cache_key = f"top:{limit}"
        cached = self._markets_cache.get(cache_key)
        if cached is not None:
            return cached

        url = (
            f"{self.base_url}/coins/markets"
            f"?vs_currency=usd&order=market_cap_desc&per_page={limit}"
            f"&page=1&sparkline=false&price_change_percentage=24h"
        )
        try:
            data = await self._get_json(url, headers=self._headers())
        except Exception as exc:
            stale = self._markets_cache.get(cache_key, allow_stale=True)
            if stale is not None:
                logger.warning("coingecko 429 — using stale markets cache")
                return stale
            logger.warning("coingecko get_top_coins failed: %s", exc)
            return []

        if not isinstance(data, list):
            return []

        self._markets_cache.set(cache_key, data)
        return data


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
