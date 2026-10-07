"""Etherscan API V2 provider for EVM contract analysis."""

from __future__ import annotations

import json
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

    async def _fetch_json(self, params: dict) -> Any:
        """Internal helper to make GET request and return the 'result' field."""
        data = await self._get_json(self.base_url, params=params)
        if str(data.get("status")) != "1":
            message = data.get("message") or "Etherscan API request failed"
            raise ProviderError(message)
        return data.get("result")

    async def get_holder_stats(self, address: str, chain: str) -> dict[str, Any]:
        """Fetches top 10 holder concentration using Etherscan V2 tokenholderlist and tokensupply endpoints."""
        if not self.api_key:
            logger.warning("etherscan holder stats skipped: ETHERSCAN_API_KEY is not configured")
            raise ProviderError("ETHERSCAN_API_KEY is not configured")

        chain_id = CHAIN_IDS.get((chain or "").lower())
        if not chain_id:
            logger.warning("etherscan unsupported chain: %s", chain)
            raise ProviderError(f"Unsupported EVM chain for Etherscan: {chain}")

        try:
            # 1. Fetch Top 10 Holders (Free tier allows this subset)
            holders = await self._fetch_json({
                "chainid": chain_id,
                "module": "token",
                "action": "tokenholderlist",
                "contractaddress": address,
                "page": 1,
                "offset": 10,
                "apikey": self.api_key,
            })

            if not holders:
                return {"top_10_holder_pct": "Unknown", "reason": "No holders indexed yet"}

            # 2. Fetch Total Supply to calculate percentage
            total_supply_str = await self._fetch_json({
                "chainid": chain_id,
                "module": "stats",
                "action": "tokensupply",
                "contractaddress": address,
                "apikey": self.api_key,
            })

            if total_supply_str and float(total_supply_str) > 0:
                total_supply = float(total_supply_str)
                top_10_amount = sum(float(h.get("TokenHolderAmount", 0)) for h in holders)
                pct = (top_10_amount / total_supply) * 100
                return {"top_10_holder_pct": f"{pct:.2f}%", "holders_found": len(holders)}
            else:
                return {"top_10_holder_pct": "Unknown", "reason": "Total supply is 0 or unknown"}

        except Exception as e:
            logger.warning("Failed to calculate holder concentration for %s on %s: %s", address, chain, e)
            return {"top_10_holder_pct": "Unknown", "error": str(e)}

    async def get_contract_analysis(self, address: str, chain: str) -> dict[str, Any]:
        if not self.api_key:
            logger.warning("etherscan contract analysis skipped: ETHERSCAN_API_KEY is not configured")
            raise ProviderError("ETHERSCAN_API_KEY is not configured")
            
        chain_id = CHAIN_IDS.get((chain or "").lower())
        if not chain_id:
            logger.warning("etherscan unsupported chain: %s", chain)
            raise ProviderError(f"Unsupported EVM chain for Etherscan: {chain}")

        # 1. Fetch Contract Source Code
        try:
            source_result = await self._fetch_json({
                "chainid": chain_id,
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": self.api_key,
            })
        except ProviderError as e:
            logger.error("etherscan getsourcecode failed for %s on %s: %s", address, chain, e)
            raise

        if not source_result:
            logger.warning("etherscan returned no contract data for %s on %s", address, chain)
            raise ProviderError("Etherscan returned no contract data")

        contract_info = source_result[0]

        # 2. Parse ABI (Try getsourcecode first, fallback to getabi if needed)
        abi_string = contract_info.get("ABI", "[]")
        abi_methods = []
        if abi_string != "Contract source code not verified":
            try:
                abi_methods = json.loads(abi_string)
            except json.JSONDecodeError:
                logger.warning("Failed to parse ABI from getsourcecode, falling back to getabi.")
                try:
                    abi_result = await self._fetch_json({
                        "chainid": chain_id,
                        "module": "contract",
                        "action": "getabi",
                        "address": address,
                        "apikey": self.api_key,
                    })
                    abi_methods = json.loads(abi_result)
                except Exception as e:
                    logger.warning("Failed to fetch/parse ABI for %s: %s", address, e)

        # 3. Fetch Holder Stats concurrently using get_holder_stats
        holder_stats = await self.get_holder_stats(address, chain)

        # 4. Analyze ABI for security flags
        mint_function = False
        blacklist_function = False
        has_renounce_function = False
        proxy_upgradeable = False

        if abi_methods:
            for method in abi_methods:
                name = method.get("name", "").lower()
                # Mint Detection
                if name in ("mint", "minttoken", "minttokens", "issue", "mintfor"):
                    mint_function = True
                # Blacklist Detection
                if any(x in name for x in ("blacklist", "whitelist", "blocklist", "ban", "freeze", "exclude")):
                    blacklist_function = True
                # Ownership Renounce Function Detection
                if name in ("renounceownership",):
                    has_renounce_function = True
                # Proxy/Upgradeable Detection
                if any(x in name for x in ("upgradeto", "upgradetoandcall", "implementation", "setimplementation", "setproxy")):
                    proxy_upgradeable = True

        # Check Proxy flag explicitly returned by Etherscan getsourcecode
        if contract_info.get("Proxy") == "1" or contract_info.get("Implementation"):
            proxy_upgradeable = True

        # 5. Verification status
        is_verified = (
            contract_info.get("ABI") != "Contract source code not verified" 
            and contract_info.get("SourceCode", "").strip() != ""
        )

        # 6. Merge with existing analyzer logic
        # (Assuming analyze_contract_payload does some initial parsing like compiler version etc)
        analysis = analyze_contract_payload(contract_info)

        # 7. Update the analysis dict with our deep analysis
        analysis.update({
            "provider": self.name,
            "chain": chain,
            "chain_id": chain_id,
            "top_10_holder_pct": holder_stats.get("top_10_holder_pct", "Unknown"),
            "contract_verification": is_verified,
            # Etherscan can only see if the function exists, not if it was called.
            "ownership_renounced": "Unknown (Requires RPC)" if has_renounce_function else False,
            "mint_function": mint_function,
            "blacklist_function": blacklist_function,
            # Etherscan cannot simulate trades to detect honeypots or taxes
            "honeypot_check": "Unknown (Requires GoPlus API)",
            "proxy_upgradeable": proxy_upgradeable,
            "buy_sell_tax": "Unknown (Requires GoPlus API)",
        })
        
        return analysis
