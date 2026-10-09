"""Market and prices handlers (multilingual)."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t
from providers.coingecko import CoinGeckoProvider

router = Router(name="market")


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


def _money(value) -> str:
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if v >= 1000:
        return f"${v:,.0f}"
    if v >= 1:
        return f"${v:,.2f}"
    return f"${v:.6f}".rstrip("0").rstrip(".")


def _percent(value) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def _change(value) -> str:
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    arrow = "📈" if v >= 0 else "📉"
    return f"{arrow} {v:+.2f}%"


@router.message(Command("market"))
@router.callback_query(lambda callback: callback.data == "m:market")
async def market_handler(
    event: Message | CallbackQuery,
    db: Database,
    coingecko: CoinGeckoProvider,
) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    user_id = event.from_user.id
    lang = await _get_lang(user_id, db)

    market_cap = None
    btc_dominance = None

    # Essai 1 : /global
    try:
        data = await coingecko.get_global_market()
        market_cap = (data.get("total_market_cap") or {}).get("usd")
        btc_dominance = (data.get("market_cap_percentage") or {}).get("btc")
    except Exception:
        data = None

    # Essai 2 (fallback) : on calcule depuis /coins/markets
    if market_cap is None:
        try:
            coins = await coingecko.get_top_coins(limit=10)
            if coins:
                market_cap = sum(
                    (c.get("market_cap") or 0) for c in coins if isinstance(c.get("market_cap"), (int, float))
                )
                btc = next((c for c in coins if (c.get("symbol") or "").lower() == "btc"), None)
                if btc and btc.get("market_cap") and market_cap:
                    btc_dominance = (btc["market_cap"] / market_cap) * 100
        except Exception:
            pass

    if market_cap is None and btc_dominance is None:
        text = t("scan_unavailable", lang)
    else:
        text = (
            t("market_header", lang)
            + t("market_total_cap", lang, value=_money(market_cap))
            + "\n"
            + t("market_btc_dominance", lang, value=_percent(btc_dominance))
        )

    if isinstance(event, CallbackQuery):
        await message.edit_text(text, parse_mode="HTML", reply_markup=back_only(lang=lang))
        await event.answer()
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=back_only(lang=lang))


@router.message(Command("prices"))
async def prices_handler(message: Message, db: Database, coingecko: CoinGeckoProvider) -> None:
    lang = await _get_lang(message.from_user.id, db)

    try:
        coins = await coingecko.get_top_coins(limit=10)
    except Exception:
        await message.answer(
            t("scan_unavailable", lang),
            reply_markup=back_only(lang=lang),
        )
        return

    if not coins:
        await message.answer(
            t("prices_unavailable", lang),
            reply_markup=back_only(lang=lang),
        )
        return

    lines = [t("prices_header", lang)]
    lines.append(t("prices_subheader", lang))

    for i, coin in enumerate(coins, start=1):
        symbol = (coin.get("symbol") or "").upper() or "?"
        price = coin.get("current_price")
        change = coin.get("price_change_percentage_24h")
        lines.append(f"{i}. <b>${symbol}</b> — {_money(price)}  {_change(change)}")

    lines.append("")
    lines.append("⚠️ <i>" + t("not_financial_advice", lang) + "</i>")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.callback_query(
    lambda callback: callback.data in {"m:trending", "m:news"}
)
async def later_phase_callback(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    await callback.message.edit_text(
        t("feature_coming_soon", lang),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )
    await callback.answer()
