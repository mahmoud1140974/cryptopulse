"""Wallet tracking handlers: /trackwallet, /mywallets, /untrackwallet, /checkwallet."""

from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only, wallets_keyboard
from config import Settings, get_plan_limits
from database.models import Database
from providers.wallet_provider import WalletProvider
from utils.formatters import escape
from utils.validators import validate_address

router = Router(name="wallets")


def _plan_of(user: dict | None) -> str:
    if not user:
        return "free"
    return str(user.get("plan") or "free").lower()


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


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


# ---------------------------------------------------------------------------
# /trackwallet <address> [chain]
# ---------------------------------------------------------------------------
@router.message(Command("trackwallet"))
async def trackwallet_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            "👛 <b>Track a wallet</b>\n\n"
            "Usage: <code>/trackwallet &lt;address&gt; [chain]</code>\n\n"
            "Examples:\n"
            "<code>/trackwallet 0xabc...</code>\n"
            "<code>/trackwallet DezXAZ... solana</code>",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    address = parts[1].strip()
    chain_hint = parts[2].strip().lower() if len(parts) >= 3 else None

    validation = validate_address(address)
    if not validation.is_valid:
        await message.answer(
            f"❌ Invalid address. {validation.reason}",
            reply_markup=back_only(),
        )
        return

    chain = chain_hint or _detect_chain(address)

    user = await db.get_or_create_user(message.from_user.id)
    plan = _plan_of(user)
    is_admin = _is_admin(message.from_user.id, settings)

    limits = get_plan_limits(plan)
    limit = limits.get("wallets_max", 0)
    if is_admin:
        limit = 999

    if limit <= 0:
        await message.answer(
            "🔒 <b>Wallet tracking is a Pro & Premium feature.</b>\n\n"
            "Track smart money wallets and get alerts when they make a move.\n\n"
            "⭐ <b>Pro</b> — track up to 3 wallets (~$5/month)\n"
            "👑 <b>Premium</b> — track up to 20 wallets (~$15/month)\n\n"
            "Use /subscribe to see all plans.",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    count = await db.count_tracked_wallets(message.from_user.id)
    if count >= limit:
        await message.answer(
            f"⚠️ <b>Wallet tracking limit reached</b>\n\n"
            f"You're tracking <b>{count}/{limit}</b> wallets.\n\n"
            "Remove one with /untrackwallet or upgrade your plan.\n\n"
            "Use /subscribe to see all plans.",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    await db.add_tracked_wallet(message.from_user.id, address, chain=chain)
    await message.answer(
        f"✅ <b>Wallet added to your tracking list.</b>\n\n"
        f"👛 <code>{address}</code>\n"
        f"⛓ Chain: <b>{chain.capitalize()}</b>\n"
        f"📊 Tracked: <b>{count + 1}/{limit}</b>\n\n"
        f"You'll be alerted when this wallet makes a move.\n"
        f"See your list with /mywallets.",
        parse_mode="HTML",
        reply_markup=back_only(),
    )


# ---------------------------------------------------------------------------
# /mywallets
# ---------------------------------------------------------------------------
@router.message(Command("mywallets"))
async def mywallets_handler(
    message: Message,
    db: Database,
    settings: Settings,
) -> None:
    user = await db.get_or_create_user(message.from_user.id)
    plan = _plan_of(user)
    limits = get_plan_limits(plan)
    limit = limits.get("wallets_max", 0)
    if _is_admin(message.from_user.id, settings):
        limit = 999

    items = await db.list_tracked_wallets(message.from_user.id, limit=100)
    if not items:
        await message.answer(
            "👛 <b>Your tracked wallets</b>\n\n"
            "No wallets yet.\n\n"
            "Add one with <code>/trackwallet &lt;address&gt;</code>",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    limit_str = "∞" if limit >= 999 else str(limit)
    lines = [f"👛 <b>Your tracked wallets</b> — {len(items)}/{limit_str}\n"]
    for i, w in enumerate(items, start=1):
        label = w.get("label") or ""
        addr = w.get("address") or ""
        chain = (w.get("chain") or "ethereum").capitalize()
        line = f"{i}. <code>{_short(addr)}</code> — {chain}"
        if label:
            line += f" ({escape(label)})"
        lines.append(line)

    lines.append("\nUse /checkwallet &lt;address&gt; to see recent activity.")
    lines.append("Remove one with /untrackwallet &lt;address&gt;.")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(),
    )


# ---------------------------------------------------------------------------
# /untrackwallet <address> [chain]
# ---------------------------------------------------------------------------
@router.message(Command("untrackwallet"))
async def untrackwallet_handler(message: Message, db: Database) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            "Usage: <code>/untrackwallet &lt;address&gt; [chain]</code>",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    address = parts[1].strip()
    chain = parts[2].strip().lower() if len(parts) >= 3 else _detect_chain(address)

    await db.remove_tracked_wallet(message.from_user.id, address, chain=chain)
    await message.answer(
        f"🗑 Removed <code>{_short(address)}</code> from your tracked wallets.",
        parse_mode="HTML",
        reply_markup=back_only(),
    )


# ---------------------------------------------------------------------------
# /checkwallet <address> [chain]
# ---------------------------------------------------------------------------
@router.message(Command("checkwallet"))
async def checkwallet_handler(
    message: Message,
    settings: Settings,
) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            "Usage: <code>/checkwallet &lt;address&gt; [chain]</code>",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    address = parts[1].strip()
    chain_hint = parts[2].strip().lower() if len(parts) >= 3 else None

    validation = validate_address(address)
    if not validation.is_valid:
        await message.answer(
            f"❌ Invalid address. {validation.reason}",
            reply_markup=back_only(),
        )
        return

    chain = chain_hint or _detect_chain(address)

    provider = WalletProvider(
        etherscan_api_key=settings.etherscan_api_key,
        helius_api_key=settings.helius_api_key,
    )

    await message.answer(
        "⏳ Fetching recent transactions…",
        reply_markup=back_only(),
    )

    txs = await provider.get_recent_transactions(address, chain=chain, limit=5)

    if not txs:
        await message.answer(
            f"⚠️ No recent transactions found for <code>{_short(address)}</code>\n"
            f"Chain: <b>{chain.capitalize()}</b>\n\n"
            "Either the wallet has no activity, or the data provider is temporarily unavailable.",
            parse_mode="HTML",
            reply_markup=back_only(),
        )
        return

    lines = [f"👛 <b>Wallet activity</b> — <code>{_short(address)}</code>"]
    lines.append(f"⛓ Chain: <b>{chain.capitalize()}</b>\n")

    for i, tx in enumerate(txs, start=1):
        direction = ""
        if tx.get("from", "").lower() == address.lower():
            direction = "📤 Out"
        elif tx.get("to", "").lower() == address.lower():
            direction = "📥 In"
        else:
            direction = "🔄 Tx"

        method = tx.get("method") or "transfer"
        if len(method) > 40:
            method = method[:37] + "..."
        value = tx.get("value_native") or 0
        when = _format_ts(tx.get("timestamp"))
        is_error = tx.get("is_error")

        line = f"{i}. {direction} — <b>{escape(method)}</b>"
        if value:
            line += f"\n   Amount: {value:.4f} native"
        line += f"\n   {when}"
        if is_error:
            line += "  ❌ failed"
        lines.append(line)

    lines.append("\n<i>Data source: Etherscan / Helius</i>")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(),
    )


# ---------------------------------------------------------------------------
# Callback: menu "Analyze Wallet"
# ---------------------------------------------------------------------------
@router.callback_query(lambda callback: callback.data == "m:wallet")
async def wallet_menu_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👛 <b>Wallet tools</b>\n\n"
        "• <code>/trackwallet &lt;address&gt;</code> — track a wallet\n"
        "• <code>/mywallets</code> — see your tracked wallets\n"
        "• <code>/checkwallet &lt;address&gt;</code> — view recent activity\n"
        "• <code>/untrackwallet &lt;address&gt;</code> — remove a wallet",
        parse_mode="HTML",
        reply_markup=wallets_keyboard(),
    )
    await callback.answer()
