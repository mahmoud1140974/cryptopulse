"""Telegram handlers package."""

from aiogram import Router

from bot.handlers import alerts, help, market, scan, start, watchlist


def get_routers() -> list[Router]:
    return [
        start.router,
        scan.router,
        watchlist.router,
        alerts.router,
        market.router,
        help.router,
    ]
