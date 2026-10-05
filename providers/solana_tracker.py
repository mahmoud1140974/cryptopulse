"""Solana token data provider with Solana Tracker and Helius fallbacks."""

from __future__ import annotations

from typing import Any

import httpx

from .base import BaseProvider, ProviderError


class SolanaTrackerProvider(BaseProvider):
    name = "solana_tracker"
    base_url = "https://data.solanatracker.io"

    def __init__(self, helius_api_key: str | None = None, timeout: float = 10.0, max_retries: int = 3) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries)
        self.helius_api_key = helius_api_key

    async def get_token_snapshot(self, address: str) -> dict[str, Any]:
        data = await self._get_json(f"{self.base_url}/tokens/{address}")
        token = data.get("token") or data
        pools = data.get("pools") or []
        primary_pool = pools[0] if pools else {}
        return {
            "provider": self.name,
            "address": address,
            "chain": "solana",
            "name": token.get("name"),
            "symbol": token.get("symbol"),
            "price_usd": _float(token.get("price") or primary_pool.get("priceUsd")),
            "liquidity_usd": _float(primary_pool.get("liquidityUsd") or data.get("liquidity")),
            "volume_24h_usd": _float(primary_pool.get("volume24h") or data.get("volume24h")),
            "market_cap_usd": _float(token.get("marketCap") or data.get("marketCap")),
            "holder_count": _int(token.get("holders") or data.get("holders")),
            "freeze_authority_active": _bool_or_none(token.get("freezeAuthority") or data.get("freezeAuthority")),
            "pair_created_at": primary_pool.get("createdAt") or token.get("createdAt"),
        }

    async def get_holder_stats(self, address: str) -> dict[str, Any]:
        """Return holder concentration when available from Solana Tracker."""
        data = await self._get_json(f"{self.base_url}/tokens/{address}/holders")
        holders = data.get("holders") or data.get("accounts") or []
        if not holders:
            raise ProviderError("Solana holder data unavailable")
        percentages = [_float(item.get("percentage") or item.get("pct")) for item in holders]
        percentages = [item for item in percentages if item is not None]
        if not percentages:
            raise ProviderError("Solana holder percentages unavailable")
        return {
            "holder_count": len(holders),
            "top10_holder_pct": sum(percentages[:10]),
            "top50_holder_pct": sum(percentages[:50]),
        }

    async def get_helius_token_accounts(self, owner_address: str) -> dict[str, Any]:
        if not self.helius_api_key:
            raise ProviderError("HELIUS_API_KEY is not configured")
        url = f"https://mainnet.helius-rpc.com/?api-key={self.helius_api_key}"
        payload = {
            "jsonrpc": "2.0",
            "id": "cryptopulse",
            "method": "getTokenAccountsByOwner",
            "params": [owner_address, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        if "error" in data:
            raise ProviderError(str(data["error"]))
        return data


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


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() not in {"", "none", "null", "false", "0"}
    return bool(value)
