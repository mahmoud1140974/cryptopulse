"""Alert handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.handlers.watchlist import track_address
from bot.keyboards import back_only
from config import Settings
from database.models import Database
from utils.formatters import escape

router = Router(name="alerts")


@router.message(Command("alerts"))
async def alerts_command(message: Message, db: Database) -> None:
    await _send_alerts(message, message.from_user.id, db, edit=False)


@router.callback_query(lambda callback: callback.data == "m:alerts")
async def alerts_menu(callback: CallbackQuery, db: Database) -> None:
    await _send_alerts(callback.message, callback.from_user.id, db, edit=True)
    await callback.answer()


@router.callback_query(lambda callback: callback.data and callback.data.startswith("a:"))
async def set_alert_callback(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    _, chain, address = callback.data.split(":", 2)
    await track_address(callback.message, callback.from_user.id, address, db, analyzer, settings, chain_hint=chain, edit=True)
    await callback.answer("Basic alerts are enabled for tracked tokens")


async def _send_alerts(message: Message, telegram_id: int, db: Database, edit: bool) -> None:
    await db.get_or_create_user(telegram_id)
    alerts = await db.list_alerts(telegram_id, limit=10)
    if not alerts:
        text = (
            "🔔 <b>Alerts</b>\n\n"
            "No alerts yet. Track a token and CryptoPulse will alert you when:\n"
            "• price changes by more than 10%\n"
            "• liquidity changes by more than 20%\n"
            "• 24h volume exceeds 3x the stored average"
        )
    else:
        lines = ["🔔 <b>Recent Alerts</b>", ""]
        for alert in alerts:
            created = str(alert.get("created_at", ""))[:16].replace("T", " ")
            lines.append(f"• <b>{escape(alert.get('alert_type', 'alert'))}</b> — {escape(created)} UTC")
        lines.append("\nUse /watchlist to manage tracked tokens.")
        text = "\n".join(lines)

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=back_only())
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=back_only())
