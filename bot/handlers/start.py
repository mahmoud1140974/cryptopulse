"""Start, main menu, and language selection handlers."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    back_only,
    change_language_keyboard,
    languages_keyboard,
    main_menu,
)
from config import Settings
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t

logger = logging.getLogger(__name__)

router = Router(name="start")


async def _ensure_user_with_admin_bypass(
    telegram_id: int,
    db: Database,
    settings: Settings,
) -> dict:
    """Crée l'utilisateur. Si admin, force Premium permanent."""
    user = await db.get_or_create_user(telegram_id)
    if settings.admin_telegram_id and telegram_id == settings.admin_telegram_id:
        current_plan = (user or {}).get("plan")
        current_expires = (user or {}).get("premium_until")
        if current_plan != "premium" or current_expires:
            try:
                await db.set_user_plan(telegram_id, "premium", None)
                user = await db.get_or_create_user(telegram_id)
            except Exception:
                pass
    return user or {}


async def _get_user_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


@router.message(Command("start", "menu"))
async def start_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    user = await _ensure_user_with_admin_bypass(message.from_user.id, db, settings)

    # Premier lancement : demander la langue
    if not user.get("language"):
        await message.answer(
            t("choose_language", DEFAULT_LANG),
            parse_mode="HTML",
            reply_markup=languages_keyboard(),
        )
        return

    lang = user.get("language") or DEFAULT_LANG
    await message.answer(
        t("welcome", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang=lang),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_initial_language(callback: CallbackQuery, db: Database) -> None:
    """Choix initial de la langue au premier démarrage."""
    code = callback.data.split(":", 1)[1]
    if not is_supported(code):
        await callback.answer("Unsupported language", show_alert=True)
        return

    await db.set_user_language(callback.from_user.id, code)

    await callback.message.edit_text(
        t("language_set", code) + "\n\n" + t("welcome", code),
        parse_mode="HTML",
        reply_markup=main_menu(lang=code),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("setlang:"))
async def change_language(callback: CallbackQuery, db: Database) -> None:
    """Changement de langue depuis /language."""
    code = callback.data.split(":", 1)[1]
    if not is_supported(code):
        await callback.answer("Unsupported language", show_alert=True)
        return

    await db.set_user_language(callback.from_user.id, code)

    await callback.message.edit_text(
        t("language_set", code),
        parse_mode="HTML",
        reply_markup=back_only(lang=code),
    )
    await callback.answer()


@router.message(Command("language", "lang"))
async def language_command(message: Message) -> None:
    await message.answer(
        t("choose_language", DEFAULT_LANG),
        parse_mode="HTML",
        reply_markup=change_language_keyboard(),
    )


@router.callback_query(lambda callback: callback.data == "m:back")
async def back_to_menu(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_user_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        t("menu_short", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang=lang),
    )
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "noop")
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(
    lambda callback: callback.data in {"m:whales", "m:settings"}
)
async def phase_placeholder(callback: CallbackQuery, db: Database) -> None:
    """Whales et Settings arrivent dans une phase ultérieure."""
    lang = await _get_user_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        t("feature_coming_soon", lang),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )
    await callback.answer()
