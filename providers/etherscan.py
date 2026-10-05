"""Etherscan API V2 provider for EVM contract analysis."""

from __future__ import annotations

import logging
from typing import Any

from analysis.contract_analyzer import analyze_contract_payload

from .base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


CHAIN_IDS = {
    "ethereum": 1,
    "bsc": 56,
    "polygon": 137,
    "arbitrum": 42161,
    "base": 8453,
}


class EtherscanProvider(BaseProvider):
    name = "etherscan"
    base_url = "https://api.etherscan.io/v2/api"

    def __init__(self, api_key: str | None = None, timeout: float = 10.0, max_retries: int = 3) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries)
        self.api_key = api_key

    async def get_contract_analysis(self, address: str, chain: str) -> dict[str, Any]:
        if not self.api_key:
            logger.warning("etherscan contract analysis skipped: ETHERSCAN_API_KEY is not configured")
            raise ProviderError("ETHERSCAN_API_KEY is not configured")
        chain_id = CHAIN_IDS.get((chain or "").lower())
        if not chain_id:
            logger.warning("etherscan unsupported chain: %s", chain)
            raise ProviderError(f"Unsupported EVM chain for Etherscan: {chain}")

        data = await self._get_json(
            self.base_url,
            params={
                "chainid": chain_id,
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": self.api_key,
            },
        )
        if str(data.get("status")) != "1":
            message = data.get("message") or "Etherscan contract lookup failed"
            logger.error("etherscan contract lookup failed for %s on %s: %s", address, chain, message)
            raise ProviderError(message)
        result = data.get("result") or []
        if not result:
            logger.warning("etherscan returned no contract data for %s on %s", address, chain)
            raise ProviderError("Etherscan returned no contract data")
        analysis = analyze_contract_payload(result[0])
        analysis.update({"provider": self.name, "chain": chain, "chain_id": chain_id})
        return analysis

    async def get_holder_stats(self, address: str, chain: str) -> dict[str, Any]:
        """Holder concentration is not reliably available on the free Etherscan tier."""
        logger.warning("etherscan holder stats unavailable for %s on %s with the free provider", address, chain)
        raise ProviderError("Holder concentration unavailable from configured free provider")
