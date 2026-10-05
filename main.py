"""CryptoPulse application entrypoint."""

from __future__ import annotations

import asyncio
import logging
import os

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

logger = logging.getLogger(__name__)


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


async def health_ok(request: web.Request) -> web.Response:
    return web.Response(text="OK", status=200)


def create_http_app(settings: Settings, bot: Bot, dp: Dispatcher) -> web.Application:
    app = web.Application()
    app.router.add_get("/", health_ok)
    app.router.add_get("/health", health_ok)

    if settings.bot_mode == "webhook":
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)

    return app


async def start_health_server(settings: Settings, bot: Bot, dp: Dispatcher) -> None:
    """Start the HTTP server required by Render health checks."""
    app = create_http_app(settings, bot, dp)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", settings.port or 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server listening on 0.0.0.0:%s", port)

    # Keep this task alive so asyncio.gather does not finish immediately.
    await asyncio.Event().wait()


async def run_telegram_bot(settings: Settings, bot: Bot, dp: Dispatcher) -> None:
    if settings.bot_mode == "webhook":
        webhook_url = settings.webhook_url.rstrip("/") + "/webhook"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        logger.info("Telegram webhook configured: %s", webhook_url)
        await asyncio.Event().wait()
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Telegram polling started")
        await dp.start_polling(bot)


async def main() -> None:
    settings = Settings.from_env()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
    settings.require_bot_token()

    bot, dp, db, scheduler = await create_app_components(settings)
    scheduler.start()

    try:
        await asyncio.gather(
            start_health_server(settings, bot, dp),
            run_telegram_bot(settings, bot, dp),
        )
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
