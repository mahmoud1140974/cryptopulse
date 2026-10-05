"""Base provider primitives with timeout, retry, logging, and consistent errors."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


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
        last_error = "unknown error"
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
                last_error = _sanitize_error(exc, params=params, headers=headers)
                logger.warning(
                    "%s request failed on attempt %s/%s: %s",
                    self.name,
                    attempt + 1,
                    self.max_retries,
                    last_error,
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(min(2**attempt, 4))
        logger.error(
            "%s request failed permanently after %s attempts: %s",
            self.name,
            self.max_retries,
            last_error,
        )
        raise ProviderError(f"{self.name} request failed: {last_error}")


def _sanitize_error(
    exc: Exception,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    message = str(exc)
    for mapping in (params or {}, headers or {}):
        for key, value in mapping.items():
            if value is None:
                continue
            if any(part in key.lower() for part in ("key", "token", "secret", "password")):
                message = message.replace(str(value), "***")
    return message
