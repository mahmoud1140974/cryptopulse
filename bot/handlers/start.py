"""Start and main menu handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only, main_menu
from config import Settings
from database.models import Database

router = Router(name="start")


async def _ensure_user_with_admin_bypass(
    telegram_id: int,
    db: Database,
    settings: Settings,
) -> None:
    """
    Crée l'utilisateur s'il n'existe pas.
    Si l'utilisateur est l'ADMIN du bot, on force le plan "premium" SANS date
    d'expiration. Ainsi l'admin a un accès total et illimité au bot.
    """
    user = await db.get_or_create_user(telegram_id)

    # Bypass admin : plan premium permanent
    if settings.admin_telegram_id and telegram_id == settings.admin_telegram_id:
        if (user or {}).get("plan") != "premium" or (user or {}).get("premium_until"):
            try:
                await db.set_user_plan(telegram_id, "premium", None)
            except Exception:
                pass


@router.message(Command("start", "menu"))
async def start_handler(message: Message, db: Database, settings: Settings) -> None:
    await _ensure_user_with_admin_bypass(message.from_user.id, db, settings)
    await message.answer(
        "👋 <b>Welcome to CryptoPulse</b>\n\n"
        "Scan crypto tokens, track risk indicators, and receive basic market alerts.\n\n"
        "Choose an option below.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.callback_query(lambda callback: callback.data == "m:back")
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👋 <b>CryptoPulse</b>\n\nChoose an option below.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "noop")
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(
    lambda callback: callback.data in {"m:wallet", "m:whales", "m:settings"}
)
async def phase_placeholder(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "This feature is planned for a later phase and is not enabled in the Phase 1 MVP.",
        reply_markup=back_only(),
    )
    await callback.answer()
