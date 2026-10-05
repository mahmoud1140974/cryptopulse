"""Watchlist handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.handlers.scan import perform_scan
from bot.keyboards import back_only, watchlist_keyboard
from config import Settings
from database.models import Database
from providers.base import ProviderError
from utils.validators import validate_address

router = Router(name="watchlist")
PAGE_SIZE = 5


async def track_address(
    message: Message,
    user_id: int,
    address: str,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    chain_hint: str | None = None,
    edit: bool = False,
) -> None:
    validation = validate_address(address)
    if not validation.is_valid:
        text = f"❌ Invalid address. {validation.reason}"
    else:
        await db.get_or_create_user(user_id)
        count = await db.count_watchlist(user_id)
        if count >= settings.free_watchlist_limit:
            text = (
                f"⚠️ Free watchlist limit reached ({settings.free_watchlist_limit} tokens).\n\n"
                "Upgrade options will be available in Phase 3."
            )
        else:
            snapshot = {}
            try:
                snapshot = await analyzer.get_market_snapshot(address, chain_hint)
            except (ProviderError, Exception):
                snapshot = {}
            chain = chain_hint or snapshot.get("chain") or validation.chain or "unknown"
            await db.add_watchlist(
                user_id,
                chain,
                address,
                symbol=snapshot.get("symbol"),
                name=snapshot.get("name"),
            )
            label = snapshot.get("symbol") or snapshot.get("name") or "token"
            text = f"✅ Added {label} to your watchlist."

    if edit:
        await message.edit_text(text, reply_markup=back_only())
    else:
        await message.answer(text, reply_markup=back_only())


@router.message(Command("track"))
async def track_command(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /track <contract>", reply_markup=back_only())
        return
    await track_address(message, message.from_user.id, parts[1].strip(), db, analyzer, settings)


@router.callback_query(lambda callback: callback.data and callback.data.startswith("t:"))
async def track_callback(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    _, chain, address = callback.data.split(":", 2)
    await track_address(callback.message, callback.from_user.id, address, db, analyzer, settings, chain_hint=chain, edit=True)
    await callback.answer()


@router.message(Command("watchlist"))
async def watchlist_command(message: Message, db: Database) -> None:
    await _send_watchlist(message, message.from_user.id, db, page=0, edit=False)


@router.callback_query(lambda callback: callback.data == "m:watchlist")
async def watchlist_menu(callback: CallbackQuery, db: Database) -> None:
    await _send_watchlist(callback.message, callback.from_user.id, db, page=0, edit=True)
    await callback.answer()


@router.callback_query(lambda callback: callback.data and callback.data.startswith("wl:"))
async def watchlist_page(callback: CallbackQuery, db: Database) -> None:
    page = int(callback.data.split(":", 1)[1])
    await _send_watchlist(callback.message, callback.from_user.id, db, page=page, edit=True)
    await callback.answer()


@router.callback_query(lambda callback: callback.data and callback.data.startswith("wr:"))
async def watchlist_remove(callback: CallbackQuery, db: Database) -> None:
    item_id = callback.data.split(":", 1)[1]
    await db.remove_watchlist(callback.from_user.id, item_id)
    await _send_watchlist(callback.message, callback.from_user.id, db, page=0, edit=True)
    await callback.answer("Removed")


@router.callback_query(lambda callback: callback.data and callback.data.startswith("ws:"))
async def watchlist_scan(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    item_id = callback.data.split(":", 1)[1]
    item = await db.get_watchlist_item(item_id)
    if not item or item.get("telegram_id") != callback.from_user.id:
        await callback.answer("Watchlist item not found", show_alert=True)
        return
    await perform_scan(callback.message, callback.from_user.id, item["contract_address"], db, analyzer, settings, edit=True)
    await callback.answer()


async def _send_watchlist(message: Message, telegram_id: int, db: Database, page: int, edit: bool) -> None:
    await db.get_or_create_user(telegram_id)
    total = await db.count_watchlist(telegram_id)
    items = await db.list_watchlist(telegram_id, limit=PAGE_SIZE, offset=page * PAGE_SIZE)
    if not items:
        text = "⭐ Your watchlist is empty.\n\nUse /track <contract> or scan a token and press Track."
    else:
        lines = [f"⭐ <b>Your Watchlist</b> — {total} token(s)", ""]
        for item in items:
            label = item.get("symbol") or item.get("name") or "Unknown token"
            lines.append(f"• <b>{label}</b> — {item.get('chain', 'unknown')}")
        text = "\n".join(lines)
    keyboard = watchlist_keyboard(items, page=page, page_size=PAGE_SIZE, total=total)
    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
