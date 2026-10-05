"""Provider fallback chain utilities."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from .base import ProviderError

logger = logging.getLogger(__name__)

ProviderCall = Callable[[], Awaitable[dict[str, Any] | None]]


@dataclass(slots=True)
class FallbackResult:
    data: dict[str, Any]
    provider: str
    errors: list[str]


class FallbackManager:
    """Try providers in order and return the first usable result."""

    async def first_success(self, calls: list[tuple[str, ProviderCall]]) -> FallbackResult:
        errors: list[str] = []
        for provider_name, call in calls:
            try:
                result = await call()
                if result:
                    return FallbackResult(data=result, provider=provider_name, errors=errors)
                message = f"{provider_name}: no data"
                logger.warning("Provider returned no data: %s", message)
                errors.append(message)
            except Exception as exc:  # provider failures must not crash the bot
                message = f"{provider_name}: {exc}"
                logger.warning("Provider failed: %s", message)
                errors.append(message)
        logger.error("All providers failed: %s", " | ".join(errors))
        raise ProviderError("All providers failed. " + " | ".join(errors))
