"""Bot middlewares, including per-user rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 10) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[int, deque[float]] = defaultdict(deque)

    def allow(self, user_id: int) -> bool:
        now = time.monotonic()
        events = self._events[user_id]
        while events and now - events[0] > self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limiter: RateLimiter | None = None) -> None:
        self.limiter = limiter or RateLimiter()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is not None and not self.limiter.allow(user_id):
            if isinstance(event, Message):
                await event.answer("⚠️ Too many requests. Please wait a few seconds and try again.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Too many requests. Please wait a few seconds.", show_alert=True)
            return None
        return await handler(event, data)
