"""Provider pour l'API GoPlus Security (détection de honeypot, taxes, top holders, etc.)."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

# Mapping des noms de chaînes courants vers les IDs de chaîne GoPlus
CHAIN_ID_MAP = {
    "eth": 1, "ethereum": 1,
    "bsc": 56, "binance-smart-chain": 56, "bnb": 56,
    "polygon": 137, "matic": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "avax": 43114, "avalanche": 43114,
    "fantom": 250, "ftm": 250,
    "base": 8453,
    "linea": 59144,
    "blast": 81457,
    "mantle": 5000,
    "scroll": 534352,
    "zksync": 324,
    "pulsechain": 369,
}


class GoPlusProvider:
    BASE_URL = "https://api.gopluslabs.io/api/v1"

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    def _get_chain_id(self, chain: str) -> str:
        """Résout l'ID de la chaîne pour l'API GoPlus."""
        if chain.isdigit():
            return chain
        return str(CHAIN_ID_MAP.get(chain.lower(), "1"))  # Défaut à Ethereum (1) si inconnu

    async def get_token_security(self, address: str, chain: str) -> dict[str, Any]:
        """
        Récupère les informations de sécurité du token (honeypot, taxes, top 10 holders, etc.).
        Ne crash jamais : renvoie un dictionnaire vide en cas d'erreur.
        """
        chain_id = self._get_chain_id(chain)
        url = f"{self.BASE_URL}/token_security/{chain_id}"
        params = {"contract_addresses": address}

        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"GoPlus API a retourné le statut {response.status} pour {address}")
                    return {}
                
                data = await response.json()

                if data.get("code") != 1:
                    logger.warning(f"GoPlus API a retourné une erreur pour {address}: {data.get('message')}")
                    return {}

                # La réponse est sous la forme: result -> { address_lower: { ... } }
                result = data.get("result", {})
                token_data = result.get(address.lower())
                if not token_data:
                    logger.warning(f"Aucune donnée GoPlus trouvée pour l'adresse {address} sur la chaîne {chain_id}.")
                    return {}

                return self._parse_token_security(token_data)

        except Exception as e:
            logger.error(f"Erreur inattendue GoPlus pour {address}: {e}")
            return {}

    @staticmethod
    def _parse_token_security(raw: dict[str, Any]) -> dict[str, Any]:
        """Extrait et formate les données pertinentes de la réponse brute GoPlus."""
        
        def to_bool(val: Any) -> bool | None:
            if val is None:
                return None
            return str(val) == "1"

        def to_float(val: Any) -> float | None:
            try:
                return float(val) if val not in (None, "", "-") else None
            except (TypeError, ValueError):
                return None

        # Calcul du pourcentage des 10 plus gros holders
        holders = raw.get("holders", [])
        top10_pct = 0.0
        if holders:
            try:
                # Trier par pourcentage décroissant
                sorted_holders = sorted(
                    holders, key=lambda h: float(h.get("percent", 0)), reverse=True
                )
                for h in sorted_holders[:10]:
                    pct = to_float(h.get("percent"))
                    if pct is not None:
                        top10_pct += pct
                
                # Normalisation : GoPlus renvoie souvent en décimal (ex: "0.1" pour 10%)
                # On vérifie la somme totale pour savoir si on doit multiplier par 100
                total_pct = sum(to_float(h.get("percent")) or 0 for h in holders)
                if 0 < total_pct <= 1.5:
                    top10_pct = top10_pct * 100.0
            except Exception:
                pass

        owner_addr = raw.get("owner_address", "")
        is_renounced = owner_addr in (
            "0x0000000000000000000000000000000000000000",
            "0x000000000000000000000000000000000000dead",
            "0x0000000000000000000000000000000000000001",
        )

        return {
            "is_honeypot": to_bool(raw.get("is_honeypot")),
            "buy_tax": to_float(raw.get("buy_tax")),
            "sell_tax": to_float(raw.get("sell_tax")),
            "top10_holders_pct": round(top10_pct, 2) if top10_pct else None,
            "owner_address": owner_addr,
            "is_renounced": is_renounced,
            "is_proxy": to_bool(raw.get("is_proxy")),
            "is_mintable": to_bool(raw.get("is_mintable")),
            "is_blacklistable": to_bool(raw.get("is_blacklisted")),
            "is_open_source": to_bool(raw.get("is_open_source")),
        }

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
