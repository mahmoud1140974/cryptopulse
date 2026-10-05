"""Market and trending placeholders for Phase 1 navigation."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only
from providers.coingecko import CoinGeckoProvider

router = Router(name="market")


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


@router.callback_query(lambda callback: callback.data in {"m:trending", "m:news"})
async def later_phase_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "This feature is planned for Phase 2 and is not enabled in the Phase 1 MVP.",
        reply_markup=back_only(),
    )
    await callback.answer()


def _money(value) -> str:
    if value is None:
        return "Data unavailable."
    return f"${float(value):,.2f}"


def _percent(value) -> str:
    if value is None:
        return "Data unavailable."
    return f"{float(value):.2f}%"
