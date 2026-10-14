"""Pump.fun scanner — fetches new Solana memecoins from Pump.fun."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

PUMPFUN_API = "https://frontend-api-v3.pump.fun"


class PumpFunScanner:
    """Fetches new tokens from Pump.fun (free public API)."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def fetch_new_tokens(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetches the newest tokens from Pump.fun."""
        url = f"{PUMPFUN_API}/coins"
        params = {
            "limit": limit,
            "sort": "created_timestamp",
            "order": "DESC",
            "includeNsfw": "false",
        }
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; CryptoPulseRadar/1.0)",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("pump.fun fetch failed: %s", exc)
            return []
        except Exception as exc:
            logger.error("pump.fun unexpected error: %s", exc)
            return []

        if not isinstance(data, list):
            logger.warning("pump.fun returned unexpected format")
            return []

        results = []
        for item in data:
            try:
                parsed = self._parse_token(item)
                if parsed:
                    results.append(parsed)
            except Exception as exc:
                logger.debug("pump.fun parse failed: %s", exc)
                continue

        return results

    @staticmethod
    def _parse_token(item: dict) -> dict[str, Any] | None:
        # Filtre sécurité : tokens bannis ou NSFW
        if item.get("is_banned") or item.get("nsfw"):
            return None

        mint = item.get("mint")
        if not mint:
            return None

        # Calcul du prix (mcap_usd / supply)
        total_supply_raw = item.get("total_supply") or 0
        decimals = item.get("base_decimals") or 6
        try:
            total_supply = float(total_supply_raw) / (10 ** int(decimals))
        except (TypeError, ValueError):
            total_supply = 0

        mcap_usd = item.get("usd_market_cap") or item.get("market_cap_usd")
        price_usd = None
        if mcap_usd and total_supply:
            try:
                price_usd = float(mcap_usd) / total_supply
            except (TypeError, ValueError):
                price_usd = None

        return {
            "address": mint,
            "chain": "solana",
            "symbol": item.get("symbol"),
            "name": item.get("name"),
            "price_usd": price_usd,
            "market_cap_usd": float(mcap_usd) if mcap_usd else None,
            "pair_created_at": item.get("created_timestamp"),
            "source": "pumpfun",
            "complete": item.get("complete", False),
            "ath_market_cap": item.get("ath_market_cap"),
            "image_uri": item.get("image_uri"),
            "twitter_url": item.get("twitter"),
            "website_url": item.get("website"),
            "is_currently_live": item.get("is_currently_live", False),
            "reply_count": item.get("reply_count", 0),
        }
