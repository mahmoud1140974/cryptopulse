"""Token analysis orchestration across free data providers."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from analysis.risk_scorer import score_token
from config import Settings
from providers.coingecko import CoinGeckoProvider
from providers.dexscreener import DexScreenerProvider
from providers.etherscan import EtherscanProvider
from providers.fallback_manager import FallbackManager
from providers.goplus import GoPlusProvider
from providers.solana_tracker import SolanaTrackerProvider
from utils.validators import validate_address


class TokenAnalyzer:
    def __init__(
        self,
        settings: Settings,
        fallback: FallbackManager | None = None,
        dexscreener: DexScreenerProvider | None = None,
        coingecko: CoinGeckoProvider | None = None,
        etherscan: EtherscanProvider | None = None,
        solana_tracker: SolanaTrackerProvider | None = None,
        goplus: GoPlusProvider | None = None,
    ) -> None:
        self.settings = settings
        self.fallback = fallback or FallbackManager()
        self.dexscreener = dexscreener or DexScreenerProvider()
        self.coingecko = coingecko or CoinGeckoProvider(settings.coingecko_api_key)
        self.etherscan = etherscan or EtherscanProvider(settings.etherscan_api_key)
        self.solana_tracker = solana_tracker or SolanaTrackerProvider(settings.helius_api_key)
        self.goplus = goplus or GoPlusProvider()

    async def analyze(self, address: str, chain_hint: str | None = None) -> dict[str, Any]:
        validation = validate_address(address)
        if not validation.is_valid:
            raise ValueError(validation.reason)

        family = validation.chain or "evm"
        snapshot_result = await self._get_snapshot(address, family, chain_hint)
        snapshot = snapshot_result.data
        chain = snapshot.get("chain") or chain_hint or family

        # Préparation des tâches asynchrones (Etherscan + GoPlus en parallèle)
        holder_task = self._safe_call(self._get_holder_stats(address, chain, family))
        contract_task = self._safe_call(self._get_contract_analysis(address, chain, family))
        goplus_task = self._safe_call(self._get_goplus_security(address, chain, family))
        
        # Exécution parallèle de toutes les requêtes d'analyse
        holder_stats, contract_analysis, goplus_security = await asyncio.gather(
            holder_task, contract_task, goplus_task
        )
        
        # Sécurité : s'assurer qu'on a bien des dictionnaires même en cas d'erreur
        holder_stats = holder_stats or {}
        contract_analysis = contract_analysis or {}
        goplus_security = goplus_security or {}

        token_age_days = _token_age_days(snapshot.get("pair_created_at"))
        
        # Fusion de toutes les données. 
        # On met goplus_security AVANT holder_stats pour que le nombre de holders 
        # précis et en temps réel de Etherscan/SolanaTracker écrase celui de GoPlus.
        merged: dict[str, Any] = {
            **snapshot,
            **goplus_security,
            **contract_analysis,
            **holder_stats,
            "chain": chain,
            "token_age_days": token_age_days,
            "snapshot_provider": snapshot_result.provider,
            "provider_errors": snapshot_result.errors,
        }
        
        # Le risk_scorer doit analyser merged["is_honeypot"] pour ajouter des points de risque lourds
        merged["risk"] = score_token(merged).as_dict()
        return merged

    async def get_market_snapshot(self, address: str, chain: str | None = None) -> dict[str, Any]:
        validation = validate_address(address)
        if not validation.is_valid:
            raise ValueError(validation.reason)
        result = await self._get_snapshot(address, validation.chain or "evm", chain)
        return result.data

    async def _get_snapshot(self, address: str, family: str, chain_hint: str | None):
        if family == "solana":
            calls = [
                ("dexscreener", lambda: self.dexscreener.get_token_snapshot(address)),
                ("solana_tracker", lambda: self.solana_tracker.get_token_snapshot(address)),
            ]
        else:
            calls = [
                ("dexscreener", lambda: self.dexscreener.get_token_snapshot(address)),
                ("coingecko", lambda: self.coingecko.get_token_snapshot(address, chain_hint)),
            ]
        return await self.fallback.first_success(calls)

    async def _get_holder_stats(self, address: str, chain: str, family: str) -> dict[str, Any]:
        if family == "solana":
            return await self.solana_tracker.get_holder_stats(address)
        return await self.etherscan.get_holder_stats(address, chain)

    async def _get_contract_analysis(self, address: str, chain: str, family: str) -> dict[str, Any]:
        if family != "evm":
            return {}
        return await self.etherscan.get_contract_analysis(address, chain)

    async def _get_goplus_security(self, address: str, chain: str, family: str) -> dict[str, Any]:
        """Appel à GoPlus (uniquement pour les chaînes EVM)."""
        if family != "evm":
            return {}
        return await self.goplus.get_token_security(address, chain)

    @staticmethod
    async def _safe_call(coro) -> dict[str, Any] | None:
        try:
            return await coro
        except Exception:
            return None


def _token_age_days(pair_created_at: Any) -> float | None:
    if pair_created_at is None:
        return None
    try:
        value = float(pair_created_at)
    except (TypeError, ValueError):
        return None
    timestamp = value / 1000 if value > 10_000_000_000 else value
    return max((time.time() - timestamp) / 86_400, 0)
