"""CryptoPulse application entrypoint."""

from __future__ import annotations

import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from alerts.alert_engine import AlertEngine
from alerts.scheduler import AlertScheduler
from analysis.token_analyzer import TokenAnalyzer
from bot.handlers import get_routers
from bot.middlewares import RateLimitMiddleware, RateLimiter
from config import Settings
from database.models import Database
from providers.coingecko import CoinGeckoProvider


async def create_app_components(settings: Settings):
    db = Database(settings)
    await db.init_schema()
    analyzer = TokenAnalyzer(settings)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp["settings"] = settings
    dp["db"] = db
    dp["analyzer"] = analyzer
    dp["coingecko"] = CoinGeckoProvider(settings.coingecko_api_key)

    limiter = RateLimiter(limit=5, window_seconds=10)
    dp.message.middleware(RateLimitMiddleware(limiter))
    dp.callback_query.middleware(RateLimitMiddleware(limiter))

    for router in get_routers():
        dp.include_router(router)

    alert_engine = AlertEngine(db, analyzer, bot=bot)
    scheduler = AlertScheduler(settings, alert_engine)
    return bot, dp, db, scheduler


async def main() -> None:
    settings = Settings.from_env()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
    settings.require_bot_token()

    bot, dp, db, scheduler = await create_app_components(settings)
    scheduler.start()

    try:
        if settings.bot_mode == "webhook":
            webhook_url = settings.webhook_url.rstrip("/") + "/webhook"
            await bot.set_webhook(webhook_url, drop_pending_updates=True)
            app = web.Application()
            app.router.add_get("/", lambda request: web.json_response({"name": "CryptoPulse", "status": "running"}))
            app.router.add_get("/health", lambda request: web.json_response({"ok": True}))
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
            setup_application(app, dp, bot=bot)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
            await site.start()
            await asyncio.Event().wait()
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
