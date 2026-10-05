"""Address and input validation helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass


EVM_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
SOLANA_BASE58_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

EVM_CHAINS = {"ethereum", "bsc", "polygon", "arbitrum", "base"}
SUPPORTED_CHAINS = EVM_CHAINS | {"solana"}


@dataclass(frozen=True, slots=True)
class AddressValidation:
    is_valid: bool
    chain: str | None
    address_type: str | None
    reason: str | None = None


def validate_address(address: str) -> AddressValidation:
    """Validate a contract or wallet address and detect its chain family."""
    cleaned = (address or "").strip()
    if EVM_ADDRESS_RE.fullmatch(cleaned):
        return AddressValidation(True, "evm", "address")
    if SOLANA_BASE58_RE.fullmatch(cleaned):
        return AddressValidation(True, "solana", "address")
    return AddressValidation(
        False,
        None,
        None,
        "Address must be an EVM address (0x + 40 hex chars) or a Solana base58 address (32–44 chars).",
    )


def normalize_chain(chain: str | None) -> str | None:
    if not chain:
        return None
    value = chain.strip().lower()
    if value == "evm":
        return "evm"
    return value if value in SUPPORTED_CHAINS else None


def chain_display_name(chain: str | None) -> str:
    names = {
        "evm": "EVM",
        "ethereum": "Ethereum",
        "bsc": "BNB Smart Chain",
        "polygon": "Polygon",
        "arbitrum": "Arbitrum",
        "base": "Base",
        "solana": "Solana",
    }
    return names.get((chain or "").lower(), "Unknown")
