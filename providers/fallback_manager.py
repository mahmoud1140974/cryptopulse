"""Provider fallback chain utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from .base import ProviderError

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
                errors.append(f"{provider_name}: no data")
            except Exception as exc:
                errors.append(f"{provider_name}: {exc}")
        raise ProviderError("All providers failed. " + " | ".join(errors))
