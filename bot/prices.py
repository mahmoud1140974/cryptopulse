"""Handler for /prices — affiche les top cryptos par capitalisation."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards import back_only
from providers.coingecko import CoinGeckoProvider

router = Router(name="prices")


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
        name = coin.get("name") or ""
        price = coin.get("current_price")
        change = coin.get("price_change_percentage_24h")

        price_str = _money(price)
        change_str = _change(change)

        lines.append(f"{i}. <b>${symbol}</b> — {price_str}  {change_str}")

    lines.append("")
    lines.append("⚠️ <i>Data from CoinGecko. Not financial advice.</i>")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_only(),
    )


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


def _change(value) -> str:
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    arrow = "📈" if v >= 0 else "📉"
    return f"{arrow} {v:+.2f}%"
