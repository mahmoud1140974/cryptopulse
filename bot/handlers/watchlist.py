"""Watchlist handlers (multilingual)."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.keyboards import back_only, watchlist_keyboard
from config import Settings, get_plan_limits
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t
from utils.validators import validate_address

router = Router(name="watchlist")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


@router.message(Command("track"))
async def track_handler(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    lang = await _get_lang(message.from_user.id, db)
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer(
            "Usage: <code>/track &lt;contract&gt;</code>",
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    address = parts[1].strip()
    validation = validate_address(address)
    if not validation.is_valid:
        await message.answer(
            t("scan_invalid_address", lang, reason=validation.reason),
            reply_markup=back_only(lang=lang),
        )
        return

    user = await db.get_or_create_user(message.from_user.id)
    plan = str((user or {}).get("plan") or "free").lower()
    limits = get_plan_limits(plan)
    limit = limits.get("watchlist_max", 5)
    if _is_admin(message.from_user.id, settings):
        limit = 999

    count = await db.count_watchlist(message.from_user.id)
    if count >= limit:
        await message.answer(
            t("watchlist_limit_reached", lang, count=count, limit=limit),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    chain = validation.chain or "ethereum"
    symbol = None
    name = None
    try:
        analysis = await analyzer.analyze(address)
        chain = analysis.get("chain") or chain
        symbol = analysis.get("symbol")
        name = analysis.get("name")
    except Exception:
        pass

    await db.add_watchlist(
        message.from_user.id, chain, address, symbol=symbol, name=name
    )

    await message.answer(
        t("watchlist_added", lang, symbol=symbol or address[:8]),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )


@router.message(Command("watchlist"))
async def watchlist_handler(message: Message, db: Database) -> None:
    lang = await _get_lang(message.from_user.id, db)
    items = await db.list_watchlist(message.from_user.id, limit=100)
    if not items:
        await message.answer(
            t("watchlist_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return

    lines = [t("watchlist_header", lang, count=len(items))]
    for item in items:
        label = item.get("symbol") or item.get("name") or item.get("contract_address", "")[:8]
        chain = (item.get("chain") or "unknown").capitalize()
        lines.append(f"• <b>{label}</b> — {chain}")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=watchlist_keyboard(items, lang=lang),
    )


@router.callback_query(lambda callback: callback.data and callback.data.startswith("t:"))
async def quick_track(callback: CallbackQuery, db: Database, settings: Settings) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    chain, address = parts[1], parts[2]

    user = await db.get_or_create_user(callback.from_user.id)
    plan = str((user or {}).get("plan") or "free").lower()
    limits = get_plan_limits(plan)
    limit = limits.get("watchlist_max", 5)
    if _is_admin(callback.from_user.id, settings):
        limit = 999

    count = await db.count_watchlist(callback.from_user.id)
    if count >= limit:
        await callback.answer(
            t("watchlist_limit_reached", lang, count=count, limit=limit),
            show_alert=True,
        )
        return

    await db.add_watchlist(callback.from_user.id, chain, address)
    await callback.answer(t("watchlist_added", lang, symbol=address[:8]), show_alert=False)


@router.callback_query(lambda callback: callback.data and callback.data.startswith("wr:"))
async def remove_from_watchlist(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    _, item_id = callback.data.split(":", 1)
    await db.remove_watchlist(callback.from_user.id, item_id)

    items = await db.list_watchlist(callback.from_user.id, limit=100)
    if not items:
        await callback.message.edit_text(
            t("watchlist_removed", lang) + "\n\n" + t("watchlist_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
    else:
        lines = [t("watchlist_removed", lang), "", t("watchlist_header", lang, count=len(items))]
        for item in items:
            label = item.get("symbol") or item.get("name") or item.get("contract_address", "")[:8]
            chain = (item.get("chain") or "unknown").capitalize()
            lines.append(f"• <b>{label}</b> — {chain}")
        await callback.message.edit_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=watchlist_keyboard(items, lang=lang),
        )
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "m:watchlist")
async def watchlist_menu(callback: CallbackQuery, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    items = await db.list_watchlist(callback.from_user.id, limit=100)
    if not items:
        await callback.message.edit_text(
            t("watchlist_empty", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
    else:
        lines = [t("watchlist_header", lang, count=len(items))]
        for item in items:
            label = item.get("symbol") or item.get("name") or item.get("contract_address", "")[:8]
            chain = (item.get("chain") or "unknown").capitalize()
            lines.append(f"• <b>{label}</b> — {chain}")
        await callback.message.edit_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=watchlist_keyboard(items, lang=lang),
        )
    await callback.answer()


@router.callback_query(lambda callback: callback.data and callback.data.startswith("ws:"))
async def show_watchlist_item(callback: CallbackQuery, db: Database) -> None:
    from analysis.token_analyzer import TokenAnalyzer
    from utils.formatters import format_token_report
    from bot.keyboards import result_actions

    _, item_id = callback.data.split(":", 1)
    item = await db.get_watchlist_item(item_id)
    if not item:
        await callback.answer("Not found", show_alert=True)
        return

    lang = await _get_lang(callback.from_user.id, db)

    try:
        from config import Settings
        from database.models import Database as DB
        # Fallback: scan directly
        analyzer = TokenAnalyzer(
            Settings.from_env(),
        )
        analysis = await analyzer.analyze(item["contract_address"])
        text = format_token_report(analysis, lang=lang)
        keyboard = result_actions(item.get("chain", "ethereum"), item["contract_address"], tracked=True, lang=lang)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.answer(t("error_generic", lang), show_alert=True)
    await callback.answer()
