"""Help handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only

router = Router(name="help")


HELP_TEXT = (
    "❓ <b>CryptoPulse Help</b>\n\n"

    "<b>🔍 Token Analysis</b>\n"
    "/scan &lt;contract&gt; — analyze a token\n"
    "/track &lt;contract&gt; — add a token to your watchlist\n"
    "/watchlist — show your tracked tokens\n"
    "/alerts — show recent alerts\n\n"

    "<b>📊 Market &amp; Data</b>\n"
    "/prices — top 10 cryptocurrencies\n"
    "/market — global market overview\n\n"

    "<b>💎 Subscription</b>\n"
    "/subscribe — see all plans (Free / Pro / Premium)\n"
    "/mysubscription — view your current plan\n\n"

    "<b>❓ Other</b>\n"
    "/help — show this help\n"
    "/menu — open the main menu\n\n"

    "<b>Supported chains</b>\n"
    en "EVM: Ethereum, BNB Chain, Polygon, Arbitrum, Base\n"
    "Solana\n\n"

    "<b>Supported address formats</b>\n"
    "EVM: 0x… (42 characters)\n"
    "Solana: base58 (32–44 characters)\n\n"

    "⚠️ <i>Crypto assets are highly risky. This tool provides data "
    "and risk indicators for informational purposes only and does not "
    "constitute financial advice.</i>"
)


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=back_only())


@router.callback_query(lambda callback: callback.data == "m:help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(HELP_TEXT, parse_mode="HTML", reply_markup=back_only())
    await callback.answer()
