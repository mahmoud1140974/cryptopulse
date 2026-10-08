"""Token scan handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.keyboards import back_only, result_actions
from config import Settings, get_plan_limits
from database.models import Database
from providers.base import ProviderError
from utils.formatters import format_token_report
from utils.validators import validate_address

router = Router(name="scan")


class ScanStates(StatesGroup):
    waiting_for_contract = State()


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


async def _check_scan_limit(
    user_id: int,
    plan: str,
    db: Database,
    settings: Settings,
) -> tuple[bool, str | None]:
    """
    Vérifie si l'utilisateur peut encore scanner.
    Retourne (peut_scanner, message_d_erreur_si_bloque).
    """
    # Bypass admin
    if _is_admin(user_id, settings):
        return True, None

    limits = get_plan_limits(plan)
    monthly_limit = limits.get("scans_per_month")
    daily_limit = limits.get("scans_per_day")

    # Premium : illimité
    if monthly_limit is None and daily_limit is None:
        return True, None

    # Free : limite mensuelle
    if monthly_limit is not None:
        used = await db.count_scans_this_month(user_id)
        if used >= monthly_limit:
            return False, (
                f"⚠️ <b>You've reached your monthly limit</b>\n\n"
                f"You've used <b>{used}/{monthly_limit}</b> free scans this month.\n\n"
                "Upgrade to keep scanning:\n"
                "⭐ <b>Pro</b> — 50 scans/day for ~$5/month\n"
                "👑 <b>Premium</b> — Unlimited scans for ~$15/month\n\n"
                "Use /subscribe to see all plans."
            )

    # Pro : limite journalière
    if daily_limit is not None:
        used_today = await db.count_scans_today(user_id)
        if used_today >= daily_limit:
            return False, (
                f"⚠️ <b>Daily limit reached</b>\n\n"
                f"You've used <b>{used_today}/{daily_limit}</b> scans today.\n\n"
                "Come back tomorrow, or upgrade to Premium for unlimited scans.\n\n"
                "Use /subscribe to see all plans."
            )

    return True, None


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

    user = await db.get_or_create_user(user_id)
    plan = str((user or {}).get("plan") or "free").lower()

    # Vérifie la limite selon le plan
    allowed, error_message = await _check_scan_limit(user_id, plan, db, settings)
    if not allowed:
        if edit:
            await message.edit_text(error_message, parse_mode="HTML", reply_markup=back_only())
        else:
            await message.answer(error_message, parse_mode="HTML", reply_markup=back_only())
        return

    try:
        analysis = await analyzer.analyze(address)
        await db.record_scan(
            user_id,
            analysis.get("chain") or validation.chain or "unknown",
            address,
            analysis.get("risk", {}).get("score"),
        )
        tracked = await _is_tracked(
            db, user_id, analysis.get("chain") or validation.chain or "unknown", address
        )
        text = format_token_report(analysis)
        keyboard = result_actions(
            analysis.get("chain") or validation.chain or "unknown", address, tracked=tracked
        )
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
        await message.answer(
            "🔍 Send me the token contract address you want to scan.",
            reply_markup=back_only(),
        )
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
    await perform_scan(
        message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings
    )


@router.message(lambda message: validate_address(message.text or "").is_valid)
async def scan_from_plain_address(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    await perform_scan(
        message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings
    )


@router.callback_query(lambda callback: callback.data and callback.data.startswith("r:"))
async def refresh_scan(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    _, chain, address = callback.data.split(":", 2)
    await perform_scan(
        callback.message, callback.from_user.id, address, db, analyzer, settings, edit=True
    )
    await callback.answer()


async def _is_tracked(db: Database, telegram_id: int, chain: str, address: str) -> bool:
    items = await db.list_watchlist(telegram_id, limit=100)
    return any(
        item.get("chain") == chain and item.get("contract_address") == address
        for item in items
    )
