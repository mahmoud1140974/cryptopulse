"""Help handlers (multilingual)."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t

router = Router(name="help")


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


def _help_text(lang: str) -> str:
    lines = [
        t("help_title", lang),
        "",
        t("help_section_analysis", lang),
        "/scan &lt;contract&gt; — " + t("btn_scan", lang),
        "/track &lt;contract&gt; — " + t("btn_track", lang),
        "/watchlist",
        "/alerts",
        "",
        t("help_section_market", lang),
        "/prices",
        "/market",
        "",
        t("help_section_sub", lang),
        "/subscribe",
        "/mysubscription",
        "",
        t("help_section_other", lang),
        "/help",
        "/menu",
        "",
        t("help_supported_chains", lang),
        "",
        t("help_disclaimer", lang),
    ]
    return "\n".join(lines)


@router.message(Command("help"))
async def help_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)
    await message.answer(
        _help_text(lang),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.callback_query(lambda callback: callback.data == "m:help")
async def help_callback(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        _help_text(lang),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )
    await callback.answer()
