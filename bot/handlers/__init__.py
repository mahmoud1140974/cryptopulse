"""Telegram handlers package."""

from aiogram import Router

from bot.handlers import alerts, help, market, scan, start, subscription, watchlist


def get_routers() -> list[Router]:
    return [
        start.router,
        scan.router,
        watchlist.router,
        alerts.router,
        market.router,
        subscription.router,
        help.router,
    ]
