"""Wallet tracking handlers (multilingual)."""

from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only, wallets_keyboard
from config import Settings, get_plan_limits
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t
from providers.wallet_provider import WalletProvider
from utils.formatters import escape
from utils.validators import validate_address

router = Router(name="wallets")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


def _detect_chain(address: str) -> str:
    validation = validate_address(address)
    if validation.chain == "solana":
        return "solana"
    return "ethereum"


def _short(addr: str) -> str:
    if not addr or len(addr) < 12:
        return addr or ""
    return f"{addr[:6]}…{addr[-4:]}"


def _format_ts(ts: int | None) -> str:
    if not ts:
        return "unknown"
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "unknown"


@router.message(Command("trackwallet"))
async def trackwallet_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    lang = await _get_lang(message.from_user.id, db)
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            t("wallet_usage_track", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    address = parts[1].strip()
    chain_hint = parts[2].strip().lower() if len(parts) >= 3 else None

    validation = validate_address(address)
    if not validation.is_valid:
        await message.answer(
            t("scan_invalid_address", lang, reason=validation.reason),
            reply_markup=back_only(lang=lang),
        )
        return

    chain = chain_hint or _detect_chain(address)

    user = await db.get_or_create_user(message.from_user.id)
    plan = str((user or {}).get("plan") or "free").lower()
    limits = get_plan_limits(plan)
    limit = limits.get("wallets_max", 0)
    if _is_admin(message.from_user.id, settings):
        limit = 999

    if limit <= 0:
        await message.answer(
            t("wallet_locked", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    count = await db.count_tracked_wallets(message.from_user.id)
    if count >= limit:
        await message.answer(
            t("wallet_limit_reached", lang, count=count, limit=limit),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    await db.add_tracked_wallet(message.from_user.id, address, chain=chain)
    await message.answer(
        t("wallet_added", lang, address=address, chain=chain.capitalize(), count=count + 1, limit=limit),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.message(Command("mywallets"))
async def mywallets_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    lang = await _get_lang(message.from_user.id, db)
    user = await db.get_or_create_user(message.from_user.id)
    plan = str((user or {}).get("plan") or "free").lower()
    limits = get_plan_limits(plan)
    limit = limits.get("wallets_max", 0)
    if _is_admin(message.from_user.id, settings):
        limit = 999

    items = await db.list_tracked_wallets(message.from_user.id, limit=100)
    if not items:
        await message.answer(
            t("wallet_list_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    limit_str = "∞" if limit >= 999 else str(limit)
    lines = [t("wallet_list_header", lang, count=len(items), limit=limit_str)]
    for i, w in enumerate(items, start=1):
        label = w.get("label") or ""
        addr = w.get("address") or ""
        chain = (w.get("chain") or "ethereum").capitalize()
        line = f"{i}. <code>{_short(addr)}</code> — {chain}"
        if label:
            line += f" ({escape(label)})"
        lines.append(line)

    lines.append(t("wallet_list_footer", lang))

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.message(Command("untrackwallet"))
async def untrackwallet_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            t("wallet_usage_untrack", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    address = parts[1].strip()
    chain = parts[2].strip().lower() if len(parts) >= 3 else _detect_chain(address)

    await db.remove_tracked_wallet(message.from_user.id, address, chain=chain)
    await message.answer(
        t("wallet_removed", lang, address=_short(address)),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.message(Command("checkwallet"))
async def checkwallet_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    lang = await _get_lang(message.from_user.id, db)
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            t("wallet_usage_check", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    address = parts[1].strip()
    chain_hint = parts[2].strip().lower() if len(parts) >= 3 else None

    validation = validate_address(address)
    if not validation.is_valid:
        await message.answer(
            t("scan_invalid_address", lang, reason=validation.reason),
            reply_markup=back_only(lang=lang),
        )
        return

    chain = chain_hint or _detect_chain(address)

    provider = WalletProvider(
        etherscan_api_key=settings.etherscan_api_key,
        helius_api_key=settings.helius_api_key,
    )

    await message.answer(
        t("wallet_check_fetching", lang),
        reply_markup=back_only(lang=lang),
    )

    txs = await provider.get_recent_transactions(address, chain=chain, limit=5)

    if not txs:
        await message.answer(
            t("wallet_check_no_data", lang, address=_short(address), chain=chain.capitalize()),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    lines = [t("wallet_check_header", lang, address=_short(address))]
    lines.append(t("wallet_check_chain", lang, chain=chain.capitalize()))

    for i, tx in enumerate(txs, start=1):
        direction = ""
        if tx.get("from", "").lower() == address.lower():
            direction = "📤"
        elif tx.get("to", "").lower() == address.lower():
            direction = "📥"
        else:
            direction = "🔄"

        method = tx.get("method") or "transfer"
        if len(method) > 40:
            method = method[:37] + "..."
        value = tx.get("value_native") or 0
        when = _format_ts(tx.get("timestamp"))
        is_error = tx.get("is_error")

        line = f"{i}. {direction} <b>{escape(method)}</b>"
        if value:
            line += f"\n   {value:.4f}"
        line += f"\n   {when}"
        if is_error:
            line += "  ❌"
        lines.append(line)

    lines.append(t("wallet_check_source", lang))

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.callback_query(lambda callback: callback.data == "m:wallet")
async def wallet_menu_callback(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        t("wallet_menu", lang),
        parse_mode="HTML",
        reply_markup=wallets_keyboard(lang=lang),
    )
    await callback.answer()
