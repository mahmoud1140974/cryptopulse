"""Telegram Stars payment handlers for CryptoPulse subscriptions."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from bot.keyboards import back_only
from database.models import Database

logger = logging.getLogger(__name__)
router = Router(name="payments")


# Prix en Stars (1 Star ≈ $0.013)
PAID_PLANS = {
    "pro": {
        "name": "Pro",
        "stars": 385,          # ≈ $5
        "days": 30,
        "description": "100 scans/day • 25 tokens watchlist • Alerts every 5 min • Wallet analysis",
    },
    "premium": {
        "name": "Premium",
        "stars": 1150,         # ≈ $15
        "days": 30,
        "description": "Unlimited scans • 100 tokens watchlist • Alerts every 1 min • Wallet + Whales",
    },
}


@router.callback_query(F.data.startswith("buy:"))
async def buy_callback(callback: CallbackQuery, bot: Bot) -> None:
    """Envoie la facture Telegram Stars à l'utilisateur."""
    plan_key = callback.data.split(":", 1)[1]
    plan = PAID_PLANS.get(plan_key)
    if not plan:
        await callback.answer("Unknown plan.", show_alert=True)
        return

    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"CryptoPulse {plan['name']}",
            description=plan["description"],
            payload=f"plan:{plan_key}:{plan['days']}d",
            currency="XTR",  # Telegram Stars
            prices=[
                LabeledPrice(
                    label=f"{plan['name']} — {plan['days']} days",
                    amount=plan["stars"],
                )
            ],
        )
    except Exception as exc:
        logger.error("send_invoice failed for %s: %s", plan_key, exc)
        await callback.answer(
            "⚠️ Could not start payment. Please try again in a moment.",
            show_alert=True,
        )
        return

    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery) -> None:
    """
    Valide la commande avant que Telegram ne débite l'utilisateur.
    OBLIGATOIRE : si on ne répond pas dans les 10 secondes, Telegram annule.
    """
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, db: Database) -> None:
    """Active le plan après paiement Stars réussi."""
    payment = message.successful_payment
    if payment is None:
        return

    payload = payment.invoice_payload or ""
    parts = payload.split(":")  # "plan:pro:30d"
    plan_key = parts[1] if len(parts) >= 2 else None

    days = 30
    if len(parts) >= 3:
        try:
            days = int(parts[2].rstrip("d"))
        except (TypeError, ValueError):
            days = 30

    plan = PAID_PLANS.get(plan_key or "")
    if not plan:
        logger.warning("Unknown plan in payment payload: %s", payload)
        await message.answer(
            "✅ Payment received, but the plan could not be identified. "
            "Please contact support with your payment ID."
        )
        return

    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    expires_iso = expires_at.isoformat()

    try:
        await db.set_user_plan(message.from_user.id, plan_key, expires_iso)
    except Exception as exc:
        logger.error("Failed to activate plan for %s: %s", message.from_user.id, exc)
        await message.answer(
            "✅ Payment received but activation failed. "
            "Please contact support with your transaction ID."
        )
        return

    text = (
        f"🎉 <b>Welcome to CryptoPulse {plan['name']}!</b>\n\n"
        "Your subscription is now active.\n"
        f"⏰ Expires on: <b>{expires_at.strftime('%Y-%m-%d %H:%M UTC')}</b>\n"
        f"⭐ Stars paid: {payment.total_amount}\n\n"
        "Use /mysubscription to see your plan."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=back_only())
