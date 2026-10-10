"""Token scan handlers (multilingual, with token image)."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from analysis.token_analyzer import TokenAnalyzer
from bot.keyboards import back_only, result_actions
from config import Settings, get_plan_limits
from database.models import Database
from locales import DEFAULT_LANG, is_supported, t
from providers.base import ProviderError
from utils.formatters import format_token_report
from utils.validators import validate_address

logger = logging.getLogger(__name__)
router = Router(name="scan")

# Telegram caption limit for photos is 1024 chars
CAPTION_LIMIT = 1024


class ScanStates(StatesGroup):
    waiting_for_contract = State()


def _is_admin(user_id: int, settings: Settings) -> bool:
    return bool(settings.admin_telegram_id and user_id == settings.admin_telegram_id)


async def _get_lang(telegram_id: int, db: Database) -> str:
    lang = await db.get_user_language(telegram_id)
    if lang and is_supported(lang):
        return lang
    return DEFAULT_LANG


async def _check_scan_limit(
    user_id: int,
    plan: str,
    db: Database,
    settings: Settings,
    lang: str,
) -> tuple[bool, str | None]:
    """Vérifie si l'utilisateur peut encore scanner (selon son plan)."""
    if _is_admin(user_id, settings):
        return True, None

    limits = get_plan_limits(plan)
    monthly_limit = limits.get("scans_per_month")
    daily_limit = limits.get("scans_per_day")

    if monthly_limit is None and daily_limit is None:
        return True, None

    if monthly_limit is not None:
        used = await db.count_scans_this_month(user_id)
        if used >= monthly_limit:
            return False, t(
                "scan_limit_free_reached",
                lang,
                used=used,
                limit=monthly_limit,
            )

    if daily_limit is not None:
        used_today = await db.count_scans_today(user_id)
        if used_today >= daily_limit:
            return False, t(
                "scan_limit_daily_reached",
                lang,
                used=used_today,
                limit=daily_limit,
            )

    return True, None


async def _send_report(
    message: Message,
    text: str,
    image_url: str | None,
    keyboard,
    edit: bool = False,
) -> None:
    """
    Envoie le rapport. Si une image est disponible, l'envoie en photo avec
    caption (ou photo + texte si le rapport est trop long pour un caption).
    Si edit=True (depuis Refresh), on supprime l'ancien message et on envoie
    un nouveau, car on ne peut pas éditer un message texte en photo.
    """
    # Si on doit "éditer" mais qu'on a une image, on supprime et on renvoie
    if edit:
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        except Exception:
            pass
        return

    # Cas 1 : pas d'image → envoi texte classique
    if not image_url:
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        return

    # Cas 2 : rapport court → photo avec caption
    if len(text) <= CAPTION_LIMIT:
        try:
            await message.answer_photo(
                photo=image_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return
        except Exception as exc:
            logger.warning("answer_photo with caption failed: %s", exc)
            # Fallback : photo simple + texte

    # Cas 3 : rapport long → photo séparée + texte avec boutons
    try:
        await message.answer_photo(photo=image_url)
    except Exception as exc:
        logger.warning("answer_photo (image only) failed: %s", exc)

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


async def perform_scan(
    message: Message,
    user_id: int,
    address: str,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    edit: bool = False,
) -> None:
    lang = await _get_lang(user_id, db)

    validation = validate_address(address)
    if not validation.is_valid:
        text = t("scan_invalid_address", lang, reason=validation.reason)
        if edit:
            try:
                await message.edit_text(text, reply_markup=back_only(lang=lang))
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=back_only(lang=lang))
        return

    user = await db.get_or_create_user(user_id)
    plan = str((user or {}).get("plan") or "free").lower()

    allowed, error_message = await _check_scan_limit(user_id, plan, db, settings, lang)
    if not allowed:
        if edit:
            try:
                await message.edit_text(
                    error_message, parse_mode="HTML", reply_markup=back_only(lang=lang)
                )
                return
            except Exception:
                pass
        await message.answer(
            error_message, parse_mode="HTML", reply_markup=back_only(lang=lang)
        )
        return

    try:
        analysis = await analyzer.analyze(address)
        await db.record_scan(
            user_id,
            analysis.get("chain") or validation.chain or "unknown",
            address,
            analysis.get("risk", {}).get("score"),
        )
        chain = analysis.get("chain") or validation.chain or "unknown"
        tracked = await _is_tracked(db, user_id, chain, address)
        text = format_token_report(analysis, lang=lang)
        image_url = analysis.get("image_url")
        keyboard = result_actions(chain, address, tracked=tracked, lang=lang)

        await _send_report(message, text, image_url, keyboard, edit=edit)

    except ProviderError:
        text = t("scan_unavailable", lang)
        if edit:
            try:
                await message.edit_text(text, reply_markup=back_only(lang=lang))
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=back_only(lang=lang))
    except Exception as exc:
        await db.log_error(f"Scan failed for {address}: {exc}")
        text = t("scan_unavailable", lang)
        if edit:
            try:
                await message.edit_text(text, reply_markup=back_only(lang=lang))
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=back_only(lang=lang))


@router.callback_query(lambda callback: callback.data == "m:scan")
async def scan_menu(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    lang = await _get_lang(callback.from_user.id, db)
    await state.set_state(ScanStates.waiting_for_contract)
    await callback.message.edit_text(
        t("scan_prompt", lang),
        parse_mode="HTML",
        reply_markup=back_only(lang=lang),
    )
    await callback.answer()


@router.message(Command("scan"))
async def scan_command(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    state: FSMContext,
) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        lang = await _get_lang(message.from_user.id, db)
        await state.set_state(ScanStates.waiting_for_contract)
        await message.answer(
            t("scan_prompt", lang),
            parse_mode="HTML",
            reply_markup=back_only(lang=lang),
        )
        return
    await state.clear()
    await perform_scan(message, message.from_user.id, parts[1].strip(), db, analyzer, settings)


@router.message(StateFilter(ScanStates.waiting_for_contract))
async def scan_from_state(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
    state: FSMContext,
) -> None:
    await state.clear()
    await perform_scan(
        message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings
    )


@router.message(lambda message: validate_address(message.text or "").is_valid)
async def scan_from_plain_address(
    message: Message,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    await perform_scan(
        message, message.from_user.id, (message.text or "").strip(), db, analyzer, settings
    )


@router.callback_query(lambda callback: callback.data and callback.data.startswith("r:"))
async def refresh_scan(
    callback: CallbackQuery,
    db: Database,
    analyzer: TokenAnalyzer,
    settings: Settings,
) -> None:
    _, chain, address = callback.data.split(":", 2)
    await perform_scan(
        callback.message, callback.from_user.id, address, db, analyzer, settings, edit=True
    )
    await callback.answer()


async def _is_tracked(db: Database, telegram_id: int, chain: str, address: str) -> bool:
    items = await db.list_watchlist(telegram_id, limit=100)
    return any(
        item.get("chain") == chain and item.get("contract_address") == address
        for item in items
    )
