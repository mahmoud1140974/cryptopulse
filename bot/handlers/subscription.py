"""Subscription handlers: /subscribe and /mysubscription."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only, plans_keyboard
from database.models import Database

router = Router(name="subscription")


PLANS = {
    "free": {
        "name": "Free",
        "price": "Free",
        "scans": "20 / month",
        "watchlist": "5 tokens",
        "alerts": "every 15 min",
        "wallets": "❌ Not included",
        "whales": "❌ Not included",
        "history": "7 days",
    },
    "pro": {
        "name": "Pro",
        "price": "~$5 / month (385 ⭐)",
        "scans": "50 / day",
        "watchlist": "15 tokens",
        "alerts": "every 5 min",
        "wallets": "✅ 3 wallets",
        "whales": "❌ Not included",
        "history": "30 days",
    },
    "premium": {
        "name": "Premium",
        "price": "~$15 / month (1,150 ⭐)",
        "scans": "Unlimited",
        "watchlist": "200 tokens",
        "alerts": "every 1 min",
        "wallets": "✅ 20 wallets",
        "whales": "✅ Yes",
        "history": "Unlimited",
    },
}


def _plans_text() -> str:
    lines = ["💎 <b>CryptoPulse Plans</b>", ""]

    free = PLANS["free"]
    lines.append(f"🆓 <b>{free['name']}</b> — {free['price']}")
    lines.append(f"   • Scans: {free['scans']}")
    lines.append(f"   • Watchlist: {free['watchlist']}")
    lines.append(f"   • Alerts: {free['alerts']}")
    lines.append(f"   • Wallet tracking: {free['wallets']}")
    lines.append(f"   • Whale tracking: {free['whales']}")
    lines.append(f"   • History: {free['history']}")
    lines.append("")

    pro = PLANS["pro"]
    lines.append(f"⭐ <b>{pro['name']}</b> — {pro['price']}")
    lines.append(f"   • Scans: {pro['scans']}")
    lines.append(f"   • Watchlist: {pro['watchlist']}")
    lines.append(f"   • Alerts: {pro['alerts']}")
    lines.append(f"   • Wallet tracking: {pro['wallets']}")
    lines.append(f"   • Whale tracking: {pro['whales']}")
    lines.append(f"   • History: {pro['history']}")
    lines.append("")

    prem = PLANS["premium"]
    lines.append(f"👑 <b>{prem['name']}</b> — {prem['price']}")
    lines.append(f"   • Scans: {prem['scans']}")
    lines.append(f"   • Watchlist: {prem['watchlist']}")
    lines.append(f"   • Alerts: {prem['alerts']}")
    lines.append(f"   • Wallet tracking: {prem['wallets']}")
    lines.append(f"   • Whale tracking: {prem['whales']}")
    lines.append(f"   • History: {prem['history']}")
    lines.append("")

    lines.append("💳 <i>Pay with Telegram Stars. Use the buttons below.</i>")

    return "\n".join(lines)


def _get_plan_key(user) -> str:
    try:
        if isinstance(user, dict):
            plan = user.get("plan")
        else:
            plan = getattr(user, "plan", None)
    except Exception:
        plan = None
    if not plan:
        return "free"
    return str(plan).lower()


def _get_expiry(user) -> str | None:
    try:
        if isinstance(user, dict):
            return user.get("premium_until")
        return getattr(user, "premium_until", None)
    except Exception:
        return None


@router.message(Command("subscribe"))
async def subscribe_handler(message: Message) -> None:
    await message.answer(
        _plans_text(),
        parse_mode="HTML",
        reply_markup=plans_keyboard(),
    )


@router.message(Command("mysubscription"))
async def mysubscription_handler(message: Message, db: Database) -> None:
    try:
        user = await db.get_or_create_user(message.from_user.id)
    except Exception:
        user = None

    plan_key = _get_plan_key(user)
    plan = PLANS.get(plan_key, PLANS["free"])
    expires = _get_expiry(user)

    text = (
        "👤 <b>Your Subscription</b>\n\n"
        f"Plan: <b>{plan['name']}</b>\n"
        f"Price: {plan['price']}\n"
    )
    if expires and plan_key != "free":
        text += f"⏰ Expires on: <b>{str(expires)[:10]}</b>\n"

    text += (
        "\n<b>Current limits:</b>\n"
        f"• Scans: {plan['scans']}\n"
        f"• Watchlist: {plan['watchlist']}\n"
        f"• Alerts: {plan['alerts']}\n"
        f"• Wallet tracking: {plan['wallets']}\n"
        f"• Whale tracking: {plan['whales']}\n"
        f"• History: {plan['history']}\n\n"
        "Use /subscribe to see upgrade options."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=back_only())


@router.callback_query(lambda callback: callback.data == "m:premium")
async def premium_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        _plans_text(),
        parse_mode="HTML",
        reply_markup=plans_keyboard(),
    )
    await callback.answer()
