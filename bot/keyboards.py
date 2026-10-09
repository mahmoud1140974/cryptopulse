"""Inline keyboards for CryptoPulse (multilingual)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import LANG_LABELS, t, DEFAULT_LANG


def main_menu(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_scan", lang), callback_data="m:scan")
    builder.button(text=t("btn_wallet", lang), callback_data="m:wallet")
    builder.button(text=t("btn_market", lang), callback_data="m:market")
    builder.button(text=t("btn_trending", lang), callback_data="m:trending")
    builder.button(text=t("btn_whales", lang), callback_data="m:whales")
    builder.button(text=t("btn_alerts", lang), callback_data="m:alerts")
    builder.button(text=t("btn_watchlist", lang), callback_data="m:watchlist")
    builder.button(text=t("btn_news", lang), callback_data="m:news")
    builder.button(text=t("btn_premium", lang), callback_data="m:premium")
    builder.button(text=t("btn_settings", lang), callback_data="m:settings")
    builder.button(text=t("btn_help", lang), callback_data="m:help")
    builder.adjust(2, 2, 2, 2, 2, 1)
    return builder.as_markup()


def result_actions(
    chain: str,
    address: str,
    tracked: bool = False,
    lang: str = DEFAULT_LANG,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_refresh", lang), callback_data=f"r:{chain}:{address}")
    if tracked:
        builder.button(text=t("btn_tracked", lang), callback_data="noop")
    else:
        builder.button(text=t("btn_track", lang), callback_data=f"t:{chain}:{address}")
    builder.button(text=t("btn_set_alert", lang), callback_data=f"a:{chain}:{address}")
    builder.button(text=t("btn_back", lang), callback_data="m:back")
    builder.adjust(2, 2)
    return builder.as_markup()


def watchlist_keyboard(
    items: list[dict],
    page: int = 0,
    page_size: int = 5,
    total: int | None = None,
    lang: str = DEFAULT_LANG,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        label = (
            item.get("symbol")
            or item.get("name")
            or item.get("contract_address", "Token")[:8]
        )
        builder.button(text=f"🔍 {label}", callback_data=f"ws:{item['id']}")
        builder.button(text=f"🗑 {label}", callback_data=f"wr:{item['id']}")

    total = total if total is not None else len(items)
    total_pages = max((total + page_size - 1) // page_size, 1)
    if total_pages > 1:
        builder.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
        if page > 0:
            builder.button(text="⬅️", callback_data=f"wl:{page - 1}")
        if page + 1 < total_pages:
            builder.button(text="➡️", callback_data=f"wl:{page + 1}")

    builder.button(text=t("btn_back", lang), callback_data="m:back")
    builder.adjust(2)
    return builder.as_markup()


def back_only(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_back", lang), callback_data="m:back")
    return builder.as_markup()


def plans_keyboard(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Boutons d'achat pour /subscribe."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Buy Pro — 385 ⭐", callback_data="buy:pro")
    builder.button(text="💳 Buy Premium — 1,150 ⭐", callback_data="buy:premium")
    builder.button(text=t("btn_back", lang), callback_data="m:back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def wallets_keyboard(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Clavier du menu Wallet."""
    builder = InlineKeyboardBuilder()
    builder.button(text="👛 My wallets", callback_data="w:list")
    builder.button(text=t("btn_back", lang), callback_data="m:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def languages_keyboard() -> InlineKeyboardMarkup:
    """Clavier de choix de langue (premier démarrage)."""
    builder = InlineKeyboardBuilder()
    for code, label in LANG_LABELS.items():
        builder.button(text=label, callback_data=f"lang:{code}")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def change_language_keyboard() -> InlineKeyboardMarkup:
    """Clavier de changement de langue (depuis /language)."""
    builder = InlineKeyboardBuilder()
    for code, label in LANG_LABELS.items():
        builder.button(text=label, callback_data=f"setlang:{code}")
    builder.button(text="⬅️ Back", callback_data="m:back")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()
