"""Token analysis orchestration across free data providers."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
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


_PLACEHOLDER_VALUES = {
    "", "-", "--", "n/a", "na", "unknown", "null", "none", "undefined", "nan",
}


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip().lower() in _PLACEHOLDER_VALUES:
        return False
    return True


def _merge_non_none(*sources: dict[str, Any] | None) -> dict[str, Any]:
    """
    Fusionne plusieurs dicts en ignorant None et placeholders.
    La dernière valeur UTILE gagne.
    """
    result: dict[str, Any] = {}
    for source in sources:
        if not source:
            continue
        for key, value in source.items():
            if _is_meaningful(value):
                result[key] = value
            elif key not in result:
                result[key] = value
    return result


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
        self.solana_tracker = solana_tracker or SolanaTrackerProvider(
            helius_api_key=settings.helius_api_key,
            solana_tracker_api_key=settings.solana_tracker_api_key,
        )
        self.goplus = goplus or GoPlusProvider()

    async def analyze(self, address: str, chain_hint: str | None = None) -> dict[str, Any]:
        validation = validate_address(address)
        if not validation.is_valid:
            raise ValueError(validation.reason)

        family = validation.chain or "evm"
        snapshot_result = await self._get_snapshot(address, family, chain_hint)
        snapshot = snapshot_result.data
        chain = snapshot.get("chain") or chain_hint or family

        # Récupération parallèle : holders + contrat + GoPlus
        holder_task = self._safe_call(self._get_holder_stats(address, chain, family))
        contract_task = self._safe_call(self._get_contract_analysis(address, chain, family))
        goplus_task = self._safe_call(self._get_goplus_security(address, chain, family))

        holder_stats, contract_analysis, goplus_security = await asyncio.gather(
            holder_task, contract_task, goplus_task
        )

        holder_stats = holder_stats or {}
        contract_analysis = contract_analysis or {}
        goplus_security = goplus_security or {}

        token_age_days = _token_age_days(snapshot.get("pair_created_at"))

        merged: dict[str, Any] = _merge_non_none(
            snapshot,
            goplus_security,
            contract_analysis,
            holder_stats,
        )

        merged["chain"] = chain
        merged["token_age_days"] = token_age_days
        merged["snapshot_provider"] = snapshot_result.provider
        merged["provider_errors"] = snapshot_result.errors

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
            return await self._get_snapshot_solana(address)

        calls = [
            ("dexscreener", lambda: self.dexscreener.get_token_snapshot(address)),
            ("coingecko", lambda: self.coingecko.get_token_snapshot(address, chain_hint)),
        ]
        return await self.fallback.first_success(calls)

    async def _get_snapshot_solana(self, address: str):
        """
        Pour Solana, on appelle SolanaTracker ET DexScreener EN PARALLÈLE.

        - DexScreener → prix, liquidité, volume, market cap (données de marché)
        - SolanaTracker → freeze_authority_active, holder_count (données sécurité)

        Puis on fusionne : market data de DexScreener prioritaires, security
        data de SolanaTracker non écrasées.
        """
        st_result = await self._safe_call(self.solana_tracker.get_token_snapshot(address))
        dx_result = await self._safe_call(self.dexscreener.get_token_snapshot(address))

        st = st_result or {}
        dx = dx_result or {}

        if not st and not dx:
            # Aucun provider n'a répondu : on renvoie un dict minimal pour ne pas crash
            return SimpleNamespace(
                data={"chain": "solana", "address": address},
                provider="solana_tracker+dexscreener",
                errors=["All Solana providers failed"],
            )

        # 1. Base = DexScreener (market data)
        merged: dict[str, Any] = {}
        for k, v in dx.items():
            if _is_meaningful(v):
                merged[k] = v

        # 2. Enrichissement = SolanaTracker, sauf pour les champs market
        #    où DexScreener est prioritaire s'il a déjà fourni une valeur.
        market_keys = {
            "price_usd", "liquidity_usd", "volume_24h_usd", "market_cap_usd",
            "pair_created_at", "name", "symbol",
        }
        for k, v in st.items():
            if not _is_meaningful(v):
                continue
            if k in market_keys and k in merged and _is_meaningful(merged.get(k)):
                continue
            merged[k] = v

        merged.setdefault("chain", "solana")
        merged.setdefault("address", address)

        return SimpleNamespace(
            data=merged,
            provider="solana_tracker+dexscreener",
            errors=[],
        )

    async def _get_holder_stats(self, address: str, chain: str, family: str) -> dict[str, Any]:
        if family == "solana":
            return await self.solana_tracker.get_holder_stats(address)
        return await self.etherscan.get_holder_stats(address, chain)

    async def _get_contract_analysis(self, address: str, chain: str, family: str) -> dict[str, Any]:
        if family != "evm":
            return {}
        return await self.etherscan.get_contract_analysis(address, chain)

    async def _get_goplus_security(self, address: str, chain: str, family: str) -> dict[str, Any]:
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
