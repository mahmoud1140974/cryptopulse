"""Subscription handlers: /subscribe and /mysubscription."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from database.models import Database

router = Router(name="subscription")


PLANS = {
    "free": {
        "name": "Free",
        "price": "Free",
        "scans": "10 per day",
        "watchlist": "5 tokens",
        "alerts": "every 15 min",
        "wallet": "No",
        "whales": "No",
    },
    "pro": {
        "name": "Pro",
        "price": "~$5 / month",
        "scans": "100 per day",
        "watchlist": "25 tokens",
        "alerts": "every 5 min",
        "wallet": "Yes",
        "whales": "No",
    },
    "premium": {
        "name": "Premium",
        "price": "~$15 / month",
        "scans": "Unlimited",
        "watchlist": "100 tokens",
        "alerts": "every 1 min",
        "wallet": "Yes",
        "whales": "Yes",
    },
}


def _plans_text() -> str:
    lines = ["💎 <b>CryptoPulse Plans</b>", ""]

    free = PLANS["free"]
    lines.append(f"🆓 <b>{free['name']}</b> — {free['price']}")
    lines.append(f"   • Scans: {free['scans']}")
    lines.append(f"   • Watchlist: {free['watchlist']}")
    lines.append(f"   • Alerts: {free['alerts']}")
    lines.append("")

    pro = PLANS["pro"]
    lines.append(f"⭐ <b>{pro['name']}</b> — {pro['price']}")
    lines.append(f"   • Scans: {pro['scans']}")
    lines.append(f"   • Watchlist: {pro['watchlist']}")
    lines.append(f"   • Alerts: {pro['alerts']}")
    lines.append(f"   • Wallet analysis: {pro['wallet']}")
    lines.append("")

    prem = PLANS["premium"]
    lines.append(f"👑 <b>{prem['name']}</b> — {prem['price']}")
    lines.append(f"   • Scans: {prem['scans']}")
    lines.append(f"   • Watchlist: {prem['watchlist']}")
    lines.append(f"   • Alerts: {prem['alerts']}")
    lines.append(f"   • Wallet analysis: {prem['wallet']}")
    lines.append(f"   • Whale tracking: {prem['whales']}")
    lines.append("")

    lines.append("🚧 <i>Payments are coming soon (Telegram Stars).</i>")
    lines.append("<i>You will be able to upgrade directly from this bot.</i>")

    return "\n".join(lines)


def _get_plan_key(user) -> str:
    """Récupère le plan de l'utilisateur, quoi qu'il arrive."""
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


@router.message(Command("subscribe"))
async def subscribe_handler(message: Message) -> None:
    await message.answer(
        _plans_text(),
        parse_mode="HTML",
        reply_markup=back_only(),
    )


@router.message(Command("mysubscription"))
async def mysubscription_handler(message: Message, db: Database) -> None:
    try:
        user = await db.get_or_create_user(message.from_user.id)
    except Exception:
        user = None

    plan_key = _get_plan_key(user)
    plan = PLANS.get(plan_key, PLANS["free"])

    text = (
        "👤 <b>Your Subscription</b>\n\n"
        f"Plan: <b>{plan['name']}</b>\n"
        f"Price: {plan['price']}\n\n"
        "<b>Current limits:</b>\n"
        f"• Scans: {plan['scans']}\n"
        f"• Watchlist: {plan['watchlist']}\n"
        f"• Alerts: {plan['alerts']}\n\n"
        "Use /subscribe to see upgrade options."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=back_only())


@router.callback_query(lambda callback: callback.data == "m:premium")
async def premium_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        _plans_text(),
        parse_mode="HTML",
        reply_markup=back_only(),
    )
    await callback.answer()
