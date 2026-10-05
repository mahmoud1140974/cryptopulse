"""Contract ABI and source-code risk analysis."""

from __future__ import annotations

import json
from typing import Any


RISKY_FUNCTION_KEYWORDS = {
    "mint": "Mint function detected in contract",
    "blacklist": "Blacklist function detected in contract",
    "pause": "Pause function detected in contract",
    "setfee": "Fee modification function detected in contract",
    "settax": "Tax modification function detected in contract",
}

ZERO_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}


def parse_abi(raw_abi: Any) -> list[dict[str, Any]]:
    if isinstance(raw_abi, list):
        return [item for item in raw_abi if isinstance(item, dict)]
    if not isinstance(raw_abi, str) or not raw_abi.strip():
        return []
    try:
        parsed = json.loads(raw_abi)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def analyze_contract_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize Etherscan-style source data into risk inputs."""
    payload = payload or {}
    abi = parse_abi(payload.get("ABI"))
    function_names = {
        str(item.get("name", "")).lower()
        for item in abi
        if item.get("type") == "function"
    }

    detected = set()
    for name in function_names:
        for keyword in RISKY_FUNCTION_KEYWORDS:
            if keyword in name:
                detected.add(keyword)

    source_code = payload.get("SourceCode") or ""
    contract_name = payload.get("ContractName")
    verified = bool(contract_name and source_code and str(payload.get("ABI")) != "Contract source code not verified")
    proxy_value = str(payload.get("Proxy", "0")).lower()
    is_proxy = proxy_value in {"1", "true", "yes"} or "proxy" in source_code.lower()
    owner = str(payload.get("Owner") or payload.get("owner") or "").lower()

    return {
        "contract_name": contract_name or None,
        "contract_verified": verified,
        "has_mint": "mint" in detected,
        "has_blacklist": "blacklist" in detected,
        "has_pause": "pause" in detected,
        "has_fee_modification": "setfee" in detected or "settax" in detected,
        "is_proxy": is_proxy,
        "owner": owner or None,
        "ownership_renounced": owner in ZERO_ADDRESSES if owner else None,
        "risk_messages": [RISKY_FUNCTION_KEYWORDS[key] for key in sorted(detected)],
    }
