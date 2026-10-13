"""Radar scanner — fetches new memecoin pools from GeckoTerminal."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GECKO_TERMINAL_BASE = "https://api.geckoterminal.com/api/v2"

NETWORKS = ["eth", "solana", "bsc", "base"]

NETWORK_TO_CHAIN = {
    "eth": "ethereum",
    "solana": "solana",
    "bsc": "bsc",
    "base": "base",
    "polygon_pos": "polygon",
    "arbitrum": "arbitrum",
}


class RadarScanner:
    """Fetches new pools from GeckoTerminal (free, no key required)."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def fetch_new_pools(self, network: str, limit: int = 20) -> list[dict[str, Any]]:
        """Fetch the newest pools on a network."""
        url = f"{GECKO_TERMINAL_BASE}/networks/{network}/new_pools"
        headers = {"Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("geckoterminal failed for %s: %s", network, exc)
            return []
        except Exception as exc:
            logger.error("geckoterminal unexpected error for %s: %s", network, exc)
            return []

        pools = data.get("data") or []
        chain = NETWORK_TO_CHAIN.get(network, network)

        result = []
        for pool in pools[:limit]:
            try:
                parsed = self._parse_pool(pool, chain)
                if parsed:
                    result.append(parsed)
            except Exception as exc:
                logger.debug("parse pool failed: %s", exc)
                continue

        return result

    @staticmethod
    def _parse_pool(pool: dict, chain: str) -> dict[str, Any] | None:
        attributes = pool.get("attributes") or {}
        relationships = pool.get("relationships") or {}

        base_token = (relationships.get("base_token") or {}).get("data") or {}
        base_id = base_token.get("id") or ""

        if "_" not in base_id:
            return None
        token_address = base_id.split("_", 1)[1]
        if not token_address:
            return None

        pool_name = attributes.get("name") or ""
        base_symbol = pool_name.split("/")[0].strip() if "/" in pool_name else ""

        created_at_iso = attributes.get("pool_created_at")
        created_ms = None
        if created_at_iso:
            try:
                dt = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
                created_ms = int(dt.timestamp() * 1000)
            except Exception:
                created_ms = None

        def _f(val: Any) -> float | None:
            if val is None or val == "":
                return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        price_usd = _f(attributes.get("base_token_price_usd"))
        liquidity_usd = _f(attributes.get("reserve_in_usd"))
        fdv_usd = _f(attributes.get("fdv_usd"))
        mcap_usd = _f(attributes.get("market_cap_usd"))

        volume_24h = None
        vol_data = attributes.get("volume_usd") or {}
        if isinstance(vol_data, dict):
            volume_24h = _f(vol_data.get("h24"))

        return {
            "address": token_address,
            "chain": chain,
            "symbol": base_symbol or None,
            "pool_address": attributes.get("address"),
            "price_usd": price_usd,
            "liquidity_usd": liquidity_usd,
            "volume_24h_usd": volume_24h,
            "market_cap_usd": mcap_usd or fdv_usd,
            "pair_created_at": created_ms,
        }
