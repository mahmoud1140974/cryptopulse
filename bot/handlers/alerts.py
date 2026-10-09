"""Alerts handlers (multilingual)."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t

router = Router(name="alerts")


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


def _format_alert_line(alert: dict, lang: str) -> str:
    """Formate une ligne d'alerte."""
    atype = alert.get("alert_type") or "alert"
    created = str(alert.get("created_at") or "")[:16].replace("T", " ")
    return f"• <b>{atype}</b> — {created}"


@router.message(Command("alerts"))
async def alerts_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)

    try:
        items = await db.list_alerts(message.from_user.id, limit=10)
    except Exception:
        items = []

    if not items:
        await message.answer(
            t("alerts_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    lines = [t("alerts_header", lang)]
    for alert in items:
        lines.append(_format_alert_line(alert, lang))

    lines.append("")
    lines.append("/watchlist")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.callback_query(lambda callback: callback.data == "m:alerts")
async def alerts_callback(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)

    try:
        items = await db.list_alerts(callback.from_user.id, limit=10)
    except Exception:
        items = []

    if not items:
        await callback.message.edit_text(
            t("alerts_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
    else:
        lines = [t("alerts_header", lang)]
        for alert in items:
            lines.append(_format_alert_line(alert, lang))
        lines.append("")
        lines.append("/watchlist")

        await callback.message.edit_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
    await callback.answer()
