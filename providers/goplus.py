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

# Adresses considérées comme "renoncées" (burn address, zero address, dead)
_RENOUNCED_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
    "0x0000000000000000000000000000000000000001",
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
        return str(CHAIN_ID_MAP.get(chain.lower(), "1"))  # Défaut à Ethereum

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
                    logger.warning(
                        "GoPlus API a retourné le statut %s pour %s", response.status, address
                    )
                    return {}

                data = await response.json()

                if data.get("code") != 1:
                    logger.warning(
                        "GoPlus API a retourné une erreur pour %s: %s",
                        address, data.get("message"),
                    )
                    return {}

                result = data.get("result", {})
                token_data = result.get(address.lower())
                if not token_data:
                    logger.warning(
                        "Aucune donnée GoPlus trouvée pour l'adresse %s sur la chaîne %s.",
                        address, chain_id,
                    )
                    return {}

                return self._parse_token_security(token_data)

        except Exception as e:
            logger.error("Erreur inattendue GoPlus pour %s: %s", address, e)
            return {}

    @staticmethod
    def _parse_token_security(raw: dict[str, Any]) -> dict[str, Any]:
        """Extrait et formate les données pertinentes de la réponse brute GoPlus."""

        def to_bool(val: Any) -> bool | None:
            if val is None:
                return None
            if isinstance(val, bool):
                return val
            s = str(val).strip().lower()
            if s in ("1", "true", "yes", "y"):
                return True
            if s in ("0", "false", "no", "n"):
                return False
            return None

        def to_float(val: Any) -> float | None:
            if val is None:
                return None
            s = str(val).strip()
            if s in ("", "-", "n/a", "na", "unknown", "null", "none"):
                return None
            try:
                return float(s)
            except (TypeError, ValueError):
                return None

        def to_int(val: Any) -> int | None:
            if val is None:
                return None
            s = str(val).strip()
            if s in ("", "-", "n/a", "na", "unknown", "null", "none"):
                return None
            try:
                return int(float(s))
            except (TypeError, ValueError):
                return None

        def normalize_tax(value: float | None) -> float | None:
            """GoPlus renvoie souvent un décimal (0.05 = 5%). On normalise en %."""
            if value is None:
                return None
            if value < 0:
                return None
            # Si la valeur est <= 1, c'est probablement un décimal → multiplier par 100
            if value <= 1:
                return round(value * 100, 4)
            return round(value, 4)

        # ---------- Top 10 holders ----------
        holders = raw.get("holders") or []
        top10_pct: float | None = None
        if holders:
            try:
                sorted_holders = sorted(
                    holders,
                    key=lambda h: float(h.get("percent") or 0),
                    reverse=True,
                )
                total = 0.0
                found = False
                for h in sorted_holders[:10]:
                    pct = to_float(h.get("percent"))
                    if pct is not None:
                        total += pct
                        found = True
                if found:
                    # GoPlus retourne parfois en décimal (0.37 = 37%)
                    if total <= 1.5:
                        total = total * 100.0
                    top10_pct = round(total, 2)
            except Exception:
                pass

        # ---------- Owner / renounced ----------
        owner_addr = str(raw.get("owner_address") or "").strip()
        if owner_addr and owner_addr.lower() in _RENOUNCED_ADDRESSES:
            is_renounced: bool | None = True
        elif owner_addr:
            is_renounced = False
        else:
            is_renounced = None

        # ---------- Taxes ----------
        buy_tax_raw = to_float(raw.get("buy_tax"))
        sell_tax_raw = to_float(raw.get("sell_tax"))
        buy_tax_pct = normalize_tax(buy_tax_raw)
        sell_tax_pct = normalize_tax(sell_tax_raw)

        # ---------- Contract verification ----------
        is_open_source = to_bool(raw.get("is_open_source"))

        # ---------- Mint / Blacklist ----------
        is_mintable = to_bool(raw.get("is_mintable"))
        is_blacklistable = to_bool(raw.get("is_blacklisted"))

        # On renvoie les DEUX noms (alias) pour que tous les consommateurs
        # (scorer, formatter) trouvent l'information quel que soit le nom cherché.
        return {
            # Honeypot
            "is_honeypot": to_bool(raw.get("is_honeypot")),
            "honeypot": to_bool(raw.get("is_honeypot")),

            # Taxes (format brut + format %)
            "buy_tax": buy_tax_pct,
            "buy_tax_pct": buy_tax_pct,
            "sell_tax": sell_tax_pct,
            "sell_tax_pct": sell_tax_pct,

            # Holders
            "top10_holders_pct": top10_pct,
            "top10_holder_pct": top10_pct,
            "holder_count": to_int(raw.get("holder_count")),
            "holders_count": to_int(raw.get("holder_count")),

            # Owner / renounced (2 alias)
            "owner_address": owner_addr or None,
            "is_renounced": is_renounced,
            "ownership_renounced": is_renounced,

            # Proxy / upgradeable
            "is_proxy": to_bool(raw.get("is_proxy")),
            "is_upgradeable": to_bool(raw.get("is_proxy")),

            # Mint (3 alias)
            "is_mintable": is_mintable,
            "has_mint": is_mintable,
            "can_mint": is_mintable,

            # Blacklist (3 alias)
            "is_blacklistable": is_blacklistable,
            "has_blacklist": is_blacklistable,
            "can_blacklist": is_blacklistable,

            # Vérification du contrat (2 alias)
            "is_open_source": is_open_source,
            "contract_verified": is_open_source,
        }

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
