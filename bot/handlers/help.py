"""Help handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_only

router = Router(name="help")

HELP_TEXT = (
    "❓ <b>CryptoPulse Help</b>\n\n"
    "<b>Phase 1 commands</b>\n"
    "/scan &lt;contract&gt; — scan a token contract\n"
    "/track &lt;contract&gt; — add a token to your watchlist\n"
    "/watchlist — show your tracked tokens\n"
    "/alerts — show recent alerts\n"
    "/market — market data placeholder\n"
    "/help — show this help\n\n"
    "Supported address formats: EVM 0x… and Solana base58.\n\n"
    "Crypto assets are highly risky. This tool provides data and risk indicators for informational purposes only and does not constitute financial advice."
)


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=back_only())


@router.callback_query(lambda callback: callback.data == "m:help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(HELP_TEXT, parse_mode="HTML", reply_markup=back_only())
    await callback.answer()
