"""Admin dashboard handlers (only for the bot owner)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from config import Settings
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t

logger = logging.getLogger(__name__)
router = Router(name="admin")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


def _iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _short(addr: str) -> str:
    if not addr or len(addr) < 12:
        return addr or ""
    return f"{addr[:6]}…{addr[-4:]}"


async def _build_dashboard(db: Database) -> str:
    """Construit le texte du dashboard avec toutes les stats."""
    try:
        total_users = await db.count_total_users()
        new_today = await db.count_new_users_since(_iso_days_ago(1))
        new_week = await db.count_new_users_since(_iso_days_ago(7))
        active_week = await db.count_active_users_since(_iso_days_ago(7))
        by_plan = await db.count_users_by_plan()
        by_lang = await db.count_users_by_language()
        scans_today = await db.count_scans_since(_iso_days_ago(1))
        scans_week = await db.count_scans_since(_iso_days_ago(7))
        unique_tokens = await db.count_unique_tokens_scanned()
        top_tokens = await db.top_scanned_tokens(limit=5)
    except Exception as exc:
        logger.error("admin dashboard build failed: %s", exc)
        return "⚠️ Could not load stats. Check logs."

    lines = []
    lines.append("📊 <b>ADMIN DASHBOARD</b>\n")

    lines.append("👥 <b>Users</b>")
    lines.append(f"• Total: <b>{total_users}</b>")
    lines.append(f"• New today: <b>{new_today}</b>")
    lines.append(f"• New this week: <b>{new_week}</b>")
    lines.append(f"• Active (7d): <b>{active_week}</b>")
    lines.append("")

    lines.append("💰 <b>Plans</b>")
    lines.append(f"• Free: <b>{by_plan.get('free', 0)}</b>")
    lines.append(f"• Pro: <b>{by_plan.get('pro', 0)}</b>")
    lines.append(f"• Premium: <b>{by_plan.get('premium', 0)}</b>")
    lines.append("")

    lines.append("🔍 <b>Activity</b>")
    lines.append(f"• Scans today: <b>{scans_today}</b>")
    lines.append(f"• Scans this week: <b>{scans_week}</b>")
    lines.append(f"• Unique tokens: <b>{unique_tokens}</b>")
    lines.append("")

    if top_tokens:
        lines.append("🔥 <b>Top tokens scanned</b>")
        for i, item in enumerate(top_tokens, start=1):
            lines.append(
                f"{i}. <code>{_short(item.get('address'))}</code> — "
                f"{item.get('chain')} ({item.get('count')}x)"
            )
        lines.append("")

    if by_lang:
        lines.append("🌍 <b>Languages</b>")
        lang_order = ["en", "fr", "es", "pt", "ar", "ru", "id", "tr"]
        parts = []
        for code in lang_order:
            if code in by_lang:
                parts.append(f"{code.upper()}: {by_lang[code]}")
        for code, count in by_lang.items():
            if code not in lang_order:
                parts.append(f"{code.upper()}: {count}")
        lines.append(" • ".join(parts))

    return "\n".join(lines)


@router.message(Command("admin"))
async def admin_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    # ⚠️ Access control : seul l'admin (ton ID) peut utiliser /admin
    if not _is_admin(message.from_user.id, settings):
        # On ne dit rien → message ignoré silencieusement
        return

    lang = await _get_lang(message.from_user.id, db)
    text = await _build_dashboard(db)
    await message.answer(text, parse_mode="HTML", reply_markup=back_only(lang=lang))


@router.callback_query(F.data == "m:admin")
async def admin_callback(
    callback: CallbackQuery,
    db: Database,
    settings: Settings,
) -> None:
    if not _is_admin(callback.from_user.id, settings):
        await callback.answer()
        return

    lang = await _get_lang(callback.from_user.id, db)
    text = await _build_dashboard(db)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_only(lang=lang))
    await callback.answer()
