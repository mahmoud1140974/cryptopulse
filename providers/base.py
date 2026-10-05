"""Base provider primitives with timeout, retry, and consistent errors."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx


class ProviderError(RuntimeError):
    """Raised when an external provider cannot return usable data."""


class BaseProvider:
    name = "base"

    def __init__(self, timeout: float = 10.0, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries

    async def _get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params, headers=headers)
                if response.status_code == 429 or response.status_code >= 500:
                    raise ProviderError(f"{self.name} returned HTTP {response.status_code}")
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, (dict, list)):
                    raise ProviderError(f"{self.name} returned an unsupported JSON response")
                return data
            except (httpx.HTTPError, ValueError, ProviderError) as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(min(2**attempt, 4))
        raise ProviderError(f"{self.name} request failed: {last_error}")
