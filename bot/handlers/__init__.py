"""Telegram handlers package."""

from aiogram import Router

from bot.handlers import (
    admin,
    alerts,
    help,
    market,
    payments,
    scan,
    start,
    subscription,
    wallets,
    watchlist,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        scan.router,
        watchlist.router,
        alerts.router,
        market.router,
        subscription.router,
        payments.router,
        wallets.router,
        admin.router,
        help.router,
    ]
