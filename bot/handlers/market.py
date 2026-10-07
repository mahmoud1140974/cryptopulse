"""Market handlers: /market, /prices, trending placeholder."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from providers.coingecko import CoinGeckoProvider

router = Router(name="market")


# ---------------------------------------------------------------------------
# /market
# ---------------------------------------------------------------------------
@router.message(Command("market"))
@router.callback_query(lambda callback: callback.data == "m:market")
async def market_handler(event: Message | CallbackQuery, coingecko: CoinGeckoProvider) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    try:
        data = await coingecko.get_global_market()
        market_cap = ((data.get("total_market_cap") or {}).get("usd"))
        btc_dominance = (data.get("market_cap_percentage") or {}).get("btc")
        text = (
            "📊 <b>Market Overview</b>\n\n"
            f"Total market cap: {_money(market_cap)}\n"
            f"BTC dominance: {_percent(btc_dominance)}\n\n"
            "Detailed market tools are planned for Phase 2."
        )
    except Exception:
        text = "⚠️ Some market data is temporarily unavailable. Please try again."

    if isinstance(event, CallbackQuery):
        await message.edit_text(text, parse_mode="HTML", reply_markup=back_only())
        await event.answer()
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=back_only())


# ---------------------------------------------------------------------------
# /prices — Top 10 cryptos par capitalisation boursière
# ---------------------------------------------------------------------------
@router.message(Command("prices"))
async def prices_handler(message: Message, coingecko: CoinGeckoProvider) -> None:
    try:
        coins = await coingecko.get_top_coins(limit=10)
    except Exception:
        await message.answer(
            "⚠️ Some market data is temporarily unavailable. Please try again.",
            reply_markup=back_only(),
        )
        return

    if not coins:
        await message.answer(
            "⚠️ Could not fetch top prices right now. Please try again in a minute.",
            reply_markup=back_only(),
        )
        return

    lines = ["💹 <b>Top 10 Cryptocurrencies</b>"]
    lines.append("<i>By market capitalization (CoinGecko)</i>\n")

    for i, coin in enumerate(coins, start=1):
        symbol = (coin.get("symbol") or "").upper() or "?"
        price = coin.get("current_price")
        change = coin.get("price_change_percentage_24h")
        lines.append(f"{i}. <b>${symbol}</b> — {_money(price)}  {_change(change)}")

    lines.append("")
    lines.append("⚠️ <i>Data from CoinGecko. Not financial advice.</i>")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_only())


@router.callback_query(lambda callback: callback.data in {"m:trending", "m:news"})
async def later_phase_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "This feature is planned for Phase 2 and is not enabled in the Phase 1 MVP.",
        reply_markup=back_only(),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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
        return "Data unavailable."
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "Data unavailable."


def _change(value) -> str:
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    arrow = "📈" if v >= 0 else "📉"
    return f"{arrow} {v:+.2f}%"
