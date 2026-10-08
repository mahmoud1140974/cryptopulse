"""Wallet data provider — fetches recent transactions for EVM & Solana wallets."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# Chain name → Etherscan V2 chain id
EVM_CHAIN_IDS = {
    "ethereum": 1,
    "bsc": 56,
    "polygon": 137,
    "arbitrum": 42161,
    "base": 8453,
    "optimism": 10,
    "avalanche": 43114,
}


class WalletProvider:
    """Récupère les dernières transactions d'un wallet EVM ou Solana."""

    def __init__(
        self,
        etherscan_api_key: str | None = None,
        helius_api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.etherscan_api_key = etherscan_api_key
        self.helius_api_key = helius_api_key
        self.timeout = timeout

    async def get_recent_transactions(
        self,
        address: str,
        chain: str = "ethereum",
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retourne les N dernières transactions du wallet.
        Ne crash jamais : renvoie [] en cas d'erreur.
        """
        chain_lower = (chain or "").lower()

        if chain_lower == "solana":
            return await self._get_solana_transactions(address, limit)

        chain_id = EVM_CHAIN_IDS.get(chain_lower)
        if not chain_id:
            logger.warning("wallet_provider: unsupported chain %s", chain)
            return []

        return await self._get_evm_transactions(address, chain_id, limit)

    # ------------------------------------------------------------------
    # EVM
    # ------------------------------------------------------------------
    async def _get_evm_transactions(
        self,
        address: str,
        chain_id: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        if not self.etherscan_api_key:
            logger.warning("wallet_provider: ETHERSCAN_API_KEY not configured")
            return []

        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.etherscan_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            safe = str(exc).replace(self.etherscan_api_key, "***")
            logger.error("wallet_provider Etherscan request failed: %s", safe)
            return []
        except Exception as exc:
            logger.error("wallet_provider Etherscan unexpected error: %s", exc)
            return []

        if data.get("status") != "1":
            message = data.get("message") or data.get("result") or "unknown"
            logger.warning("wallet_provider Etherscan non-OK: %s", message)
            return []

        txs = data.get("result") or []
        if not isinstance(txs, list):
            return []

        normalized: list[dict[str, Any]] = []
        for tx in txs[:limit]:
            value_wei = tx.get("value") or "0"
            try:
                value_native = int(value_wei) / 1e18
            except (TypeError, ValueError):
                value_native = 0.0
            normalized.append(
                {
                    "hash": tx.get("hash"),
                    "from": tx.get("from"),
                    "to": tx.get("to"),
                    "value_native": value_native,
                    "timestamp": _int_or_none(tx.get("timeStamp")),
                    "is_error": tx.get("isError") == "1",
                    "method": (tx.get("functionName") or "").strip() or "transfer",
                    "chain": "evm",
                }
            )
        return normalized

    # ------------------------------------------------------------------
    # Solana
    # ------------------------------------------------------------------
    async def _get_solana_transactions(
        self,
        address: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        if not self.helius_api_key:
            logger.warning("wallet_provider: HELIUS_API_KEY not configured")
            return []

        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={self.helius_api_key}&limit={limit}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            safe = str(exc).replace(self.helius_api_key, "***")
            logger.error("wallet_provider Helius request failed: %s", safe)
            return []
        except Exception as exc:
            logger.error("wallet_provider Helius unexpected error: %s", exc)
            return []

        if not isinstance(data, list):
            return []

        normalized: list[dict[str, Any]] = []
        for tx in data[:limit]:
            normalized.append(
                {
                    "hash": tx.get("signature"),
                    "from": tx.get("feePayer"),
                    "to": None,
                    "value_native": 0.0,
                    "timestamp": _int_or_none(tx.get("timestamp")),
                    "is_error": bool(tx.get("transactionError")),
                    "method": tx.get("type") or "transfer",
                    "chain": "solana",
                }
            )
        return normalized


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
