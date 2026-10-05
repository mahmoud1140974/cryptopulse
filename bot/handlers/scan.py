"""Token scan handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.keyboards import back_only, result_actions
from config import Settings
from database.models import Database
from providers.base import ProviderError
from utils.formatters import format_token_report
from utils.validators import validate_address

router = Router(name="scan")


class ScanStates(StatesGroup):
    waiting_for_contract = State()


async def perform_scan(
    message: Message,
    user_id: int,
    address: str,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    edit: bool = False,
) -> None:
    validation = validate_address(address)
    if not validation.is_valid:
        text = f"❌ Invalid address. {validation.reason}"
        if edit:
            await message.edit_text(text, reply_markup=back_only())
        else:
            await message.answer(text, reply_markup=back_only())
        return

    await db.get_or_create_user(user_id)
    scans_today = await db.count_scans_today(user_id)
    if scans_today >= settings.free_scan_limit:
        text = (
            f"⚠️ Free scan limit reached ({settings.free_scan_limit}/day).\n\n"
            "Upgrade options will be available in Phase 3."
        )
        if edit:
            await message.edit_text(text, reply_markup=back_only())
        else:
            await message.answer(text, reply_markup=back_only())
        return

    try:
        analysis = await analyzer.analyze(address)
        await db.record_scan(
            user_id,
            analysis.get("chain") or validation.chain or "unknown",
            address,
            analysis.get("risk", {}).get("score"),
        )
        tracked = await _is_tracked(db, user_id, analysis.get("chain") or validation.chain or "unknown", address)
        text = format_token_report(analysis)
        keyboard = result_actions(analysis.get("chain") or validation.chain or "unknown", address, tracked=tracked)
        if edit:
            await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    except ProviderError:
        text = "⚠️ Some market data is temporarily unavailable. Please try again."
        if edit:
            await message.edit_text(text, reply_markup=back_only())
        else:
            await message.answer(text, reply_markup=back_only())
    except Exception as exc:
        await db.log_error(f"Scan failed for {address}: {exc}")
        text = "⚠️ Some market data is temporarily unavailable. Please try again."
        if edit:
            await message.edit_text(text, reply_markup=back_only())
        else:
            await message.answer(text, reply_markup=back_only())


@router.callback_query(lambda callback: callback.data == "m:scan")
async def scan_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ScanStates.waiting_for_contract)
    await callback.message.edit_text(
        "🔍 Send me the token contract address you want to scan.\n\n"
        "Examples: an EVM address starting with 0x, or a Solana base58 address.",
        reply_markup=back_only(),
    )
    await callback.answer()


@router.message(Command("scan"))
async def scan_command(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    state: FSMContext,
) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await state.set_state(ScanStates.waiting_for_contract)
        await message.answer("🔍 Send me the token contract address you want to scan.", reply_markup=back_only())
        return
    await state.clear()
    await perform_scan(message, message.from_user.id, parts[1].strip(), db, analyzer, settings)


@router.message(StateFilter(ScanStates.waiting_for_contract))
async def scan_from_state(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    state: FSMContext,
) -> None:
    await state.clear()
    await perform_scan(message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings)


@router.message(lambda message: validate_address(message.text or "").is_valid)
async def scan_from_plain_address(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    await perform_scan(message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings)


@router.callback_query(lambda callback: callback.data and callback.data.startswith("r:"))
async def refresh_scan(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    _, chain, address = callback.data.split(":", 2)
    await perform_scan(callback.message, callback.from_user.id, address, db, analyzer, settings, edit=True)
    await callback.answer()


async def _is_tracked(db: Database, telegram_id: int, chain: str, address: str) -> bool:
    items = await db.list_watchlist(telegram_id, limit=100)
    return any(item.get("chain") == chain and item.get("contract_address") == address for item in items)
