"""Subscription handlers: /subscribe and /mysubscription (multilingual)."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only, plans_keyboard
from config import Settings
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t

router = Router(name="subscription")


PLANS = {
    "free": {
        "name_key": "🆓 Free",
        "price_key": "Free",
        "scans_key": "20 / month",
        "watchlist_key": "5 tokens",
        "alerts_key": "15 min",
        "wallets_key": "❌ Not included",
        "whales_key": "❌ Not included",
        "history_key": "7 days",
    },
    "pro": {
        "name_key": "⭐ Pro",
        "price_key": "~$5 / month (385 ⭐)",
        "scans_key": "50 / day",
        "watchlist_key": "15 tokens",
        "alerts_key": "5 min",
        "wallets_key": "✅ 3 wallets",
        "whales_key": "❌ Not included",
        "history_key": "30 days",
    },
    "premium": {
        "name_key": "👑 Premium",
        "price_key": "~$15 / month (1,150 ⭐)",
        "scans_key": "Unlimited",
        "watchlist_key": "200 tokens",
        "alerts_key": "1 min",
        "wallets_key": "✅ 20 wallets",
        "whales_key": "✅ Yes",
        "history_key": "Unlimited",
    },
}


def _plans_text(lang: str) -> str:
    lines = [t("subscribe_title", lang), ""]

    labels = {
        "en": {
            "scans": "Scans", "watchlist": "Watchlist", "alerts": "Alerts",
            "wallets": "Wallet tracking", "whales": "Whale tracking", "history": "History",
            "pay": "💳 <i>Pay with Telegram Stars. Use the buttons below.</i>",
        },
        "fr": {
            "scans": "Scans", "watchlist": "Watchlist", "alerts": "Alertes",
            "wallets": "Suivi wallet", "whales": "Suivi baleines", "history": "Historique",
            "pay": "💳 <i>Payez avec Telegram Stars. Utilisez les boutons ci-dessous.</i>",
        },
        "es": {
            "scans": "Escaneos", "watchlist": "Lista", "alerts": "Alertas",
            "wallets": "Wallets", "whales": "Ballenas", "history": "Historial",
            "pay": "💳 <i>Paga con Telegram Stars. Usa los botones debajo.</i>",
        },
        "pt": {
            "scans": "Escaneamentos", "watchlist": "Lista", "alerts": "Alertas",
            "wallets": "Carteiras", "whales": "Baleias", "history": "Histórico",
            "pay": "💳 <i>Pague com Telegram Stars. Use os botões abaixo.</i>",
        },
        "ar": {
            "scans": "الفحوصات", "watchlist": "قائمة المتابعة", "alerts": "التنبيهات",
            "wallets": "متابعة المحافظ", "whales": "متابعة الحيتان", "history": "السجل",
            "pay": "💳 <i>ادفع عبر Telegram Stars. استخدم الأزرار أدناه.</i>",
        },
        "ru": {
            "scans": "Сканирования", "watchlist": "Список", "alerts": "Оповещения",
            "wallets": "Кошельки", "whales": "Киты", "history": "История",
            "pay": "💳 <i>Оплатите через Telegram Stars. Используйте кнопки ниже.</i>",
        },
        "id": {
            "scans": "Pemindaian", "watchlist": "Daftar", "alerts": "Peringatan",
            "wallets": "Wallet", "whales": "Paus", "history": "Riwayat",
            "pay": "💳 <i>Bayar dengan Telegram Stars. Gunakan tombol di bawah.</i>",
        },
        "tr": {
            "scans": "Taramalar", "watchlist": "İzleme", "alerts": "Uyarılar",
            "wallets": "Cüzdanlar", "whales": "Balinalar", "history": "Geçmiş",
            "pay": "💳 <i>Telegram Stars ile ödeyin. Aşağıdaki butonları kullanın.</i>",
        },
    }
    L = labels.get(lang, labels["en"])

    for key in ("free", "pro", "premium"):
        p = PLANS[key]
        lines.append(f"<b>{p['name_key']}</b> — {p['price_key']}")
        lines.append(f"   • {L['scans']}: {p['scans_key']}")
        lines.append(f"   • {L['watchlist']}: {p['watchlist_key']}")
        lines.append(f"   • {L['alerts']}: {p['alerts_key']}")
        lines.append(f"   • {L['wallets']}: {p['wallets_key']}")
        lines.append(f"   • {L['whales']}: {p['whales_key']}")
        lines.append(f"   • {L['history']}: {p['history_key']}")
        lines.append("")

    lines.append(L["pay"])
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


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


@router.message(Command("subscribe"))
async def subscribe_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)
    await message.answer(
        _plans_text(lang),
        parse_mode="HTML",
        reply_markup=plans_keyboard(lang=lang),
    )


@router.message(Command("mysubscription"))
async def mysubscription_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)

    try:
        user = await db.get_or_create_user(message.from_user.id)
    except Exception:
        user = None

    plan_key = _get_plan_key(user)
    plan = PLANS.get(plan_key, PLANS["free"])
    expires = _get_expiry(user)

    text = t("mysubscription_title", lang)
    text += t("mysubscription_plan", lang, plan=plan["name_key"]) + "\n"
    text += t("mysubscription_price", lang, price=plan["price_key"]) + "\n"
    if expires and plan_key != "free":
        text += t("mysubscription_expires", lang, date=str(expires)[:10]) + "\n"

    text += t("mysubscription_limits", lang) + "\n"
    text += f"• Scans: {plan['scans_key']}\n"
    text += f"• Watchlist: {plan['watchlist_key']}\n"
    text += f"• Alerts: {plan['alerts_key']}\n"
    text += f"• Wallet tracking: {plan['wallets_key']}\n"
    text += f"• Whale tracking: {plan['whales_key']}\n"
    text += f"• History: {plan['history_key']}\n"
    text += t("mysubscription_use", lang)

    await message.answer(text, parse_mode="HTML", reply_markup=back_only(lang=lang))


@router.callback_query(lambda callback: callback.data == "m:premium")
async def premium_callback(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        _plans_text(lang),
        parse_mode="HTML",
        reply_markup=plans_keyboard(lang=lang),
    )
    await callback.answer()
