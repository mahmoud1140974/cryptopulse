"""Sniper links — generates direct buy links for each chain."""

from __future__ import annotations

from typing import Any

# Ton compte de parrainage Jupiter (Solana)
# La clé est lue depuis les variables d'environnement, PAS en dur.
JUPITER_REFERRAL_KEY = None  # sera défini par set_jupiter_key()


def set_jupiter_key(key: str | None) -> None:
    """Appelé au démarrage pour injecter la clé depuis settings."""
    global JUPITER_REFERRAL_KEY
    JUPITER_REFERRAL_KEY = key


def get_sniper_url(address: str, chain: str) -> str | None:
    """
    Renvoie l'URL de snipe pour un token donné, selon sa chaîne.
    Retourne None si la chaîne n'est pas supportée.
    """
    if not address:
        return None

    chain_lower = (chain or "").lower()

    # --- Solana : Jupiter avec parrainage ---
    if chain_lower == "solana":
        base = f"https://jup.ag/swap/SOL-{address}"
        if JUPITER_REFERRAL_KEY:
            return f"{base}?referrer={JUPITER_REFERRAL_KEY}"
        return base

    # --- EVM : liens directs vers les DEX ---
    if chain_lower == "ethereum":
        return f"https://app.uniswap.org/#/swap?outputCurrency={address}"

    if chain_lower == "bsc":
        return f"https://pancakeswap.finance/swap?outputCurrency={address}"

    if chain_lower == "base":
        return f"https://aerodrome.finance/swap?to={address}"

    if chain_lower == "polygon":
        return f"https://quickswap.exchange/#/swap?outputCurrency={address}"

    if chain_lower == "arbitrum":
        return f"https://app.camelot.exchange/?token2={address}"

    return None


def get_sniper_label(chain: str) -> str:
    """Label du bouton selon la chaîne."""
    chain_lower = (chain or "").lower()
    if chain_lower == "solana":
        return "🚀 Sniper on Jupiter"
    if chain_lower == "ethereum":
        return "🚀 Buy on Uniswap"
    if chain_lower == "bsc":
        return "🚀 Buy on PancakeSwap"
    if chain_lower == "base":
        return "🚀 Buy on Aerodrome"
    if chain_lower == "polygon":
        return "🚀 Buy on QuickSwap"
    if chain_lower == "arbitrum":
        return "🚀 Buy on Camelot"
    return "🚀 Sniper"
