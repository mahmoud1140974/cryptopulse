"""Inline keyboards for CryptoPulse."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Scan Token", callback_data="m:scan")
    builder.button(text="👛 Analyze Wallet (PRO)", callback_data="m:wallet")
    builder.button(text="📊 Market", callback_data="m:market")
    builder.button(text="🔥 Trending", callback_data="m:trending")
    builder.button(text="🐋 Whales (PRO)", callback_data="m:whales")
    builder.button(text="🔔 Alerts", callback_data="m:alerts")
    builder.button(text="⭐ Watchlist", callback_data="m:watchlist")
    builder.button(text="📰 News", callback_data="m:news")
    builder.button(text="💎 Premium", callback_data="m:premium")
    builder.button(text="⚙️ Settings", callback_data="m:settings")
    builder.button(text="❓ Help", callback_data="m:help")
    builder.adjust(2, 2, 2, 2, 2, 1)
    return builder.as_markup()


def result_actions(chain: str, address: str, tracked: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Refresh", callback_data=f"r:{chain}:{address}")
    if tracked:
        builder.button(text="⭐ Tracked", callback_data="noop")
    else:
        builder.button(text="⭐ Track", callback_data=f"t:{chain}:{address}")
    builder.button(text="🔔 Set Alert", callback_data=f"a:{chain}:{address}")
    builder.button(text="⬅️ Back", callback_data="m:back")
    builder.adjust(2, 2)
    return builder.as_markup()


def watchlist_keyboard(items: list[dict], page: int = 0, page_size: int = 5, total: int | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        label = item.get("symbol") or item.get("name") or item.get("contract_address", "Token")[:8]
        builder.button(text=f"🔍 {label}", callback_data=f"ws:{item['id']}")
        builder.button(text=f"🗑 Remove {label}", callback_data=f"wr:{item['id']}")

    total = total if total is not None else len(items)
    total_pages = max((total + page_size - 1) // page_size, 1)
    if total_pages > 1:
        builder.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
        if page > 0:
            builder.button(text="⬅️ Prev", callback_data=f"wl:{page - 1}")
        if page + 1 < total_pages:
            builder.button(text="Next ➡️", callback_data=f"wl:{page + 1}")

    builder.button(text="⬅️ Back", callback_data="m:back")
    builder.adjust(2)
    return builder.as_markup()


def back_only() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Back", callback_data="m:back")
    return builder.as_markup()
