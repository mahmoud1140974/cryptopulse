"""Radar bot — scans, filters, posts to the Telegram channel."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from analysis.token_analyzer import TokenAnalyzer
from config import Settings
from radar.filter import apply_filters, calculate_signal
from radar.formatter import (
    format_daily_recap,
    format_daily_stats,
    format_new_token_post,
    format_tip_of_the_day,
    format_update_post,
)
from radar.scanner import RadarScanner
from radar.storage import RadarStorage

logger = logging.getLogger(__name__)


class RadarBot:
    def __init__(
        self,
        settings: Settings,
        analyzer: TokenAnalyzer,
        bot_token: str,
        channel_id: str,
    ) -> None:
        self.settings = settings
        self.analyzer = analyzer
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.bot = Bot(
            bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.scanner = RadarScanner()
        self.storage = RadarStorage(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
        self.scheduler = AsyncIOScheduler()

        # Compteurs du jour
        self.today_stats = {"scanned": 0, "posted": 0, "buy": 0, "watch": 0, "avoid": 0}
        self.today_tokens: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Job 1 : scan & post (toutes les 15 min)
    # ------------------------------------------------------------------
    async def scan_and_post(self) -> dict[str, int]:
        """Scanne les nouveaux pools, filtre, poste."""
        logger.info("Radar: scan started")

        try:
            pools = await self.scanner.fetch_all_networks(limit_per_network=20)
        except Exception as exc:
            logger.error("Radar: scanner failed: %s", exc)
            return {"posted": 0, "errors": 1}

        posted = 0
        self.today_stats["scanned"] += len(pools)

        for pool in pools:
            try:
                address = pool.get("address")
                chain = pool.get("chain")
                if not address or not chain:
                    continue

                # Anti-doublon
                if await self.storage.already_posted(address, chain):
                    continue

                # Analyse complète (prix, holders, honeypot, etc.)
                try:
                    analysis = await self.analyzer.analyze(address, chain_hint=chain)
                except Exception as exc:
                    logger.debug("analyze failed for %s: %s", address, exc)
                    continue

                # Fusionne les données du pool (variations) avec l'analyse
                for k in ("price_change_h1", "price_change_h6", "price_change_h24"):
                    if pool.get(k) is not None:
                        analysis[k] = pool[k]
                if pool.get("pair_created_at") and not analysis.get("pair_created_at"):
                    analysis["pair_created_at"] = pool.get("pair_created_at")

                # Filtres qualité + anti-pump
                passed, reason = apply_filters(analysis)
                if not passed:
                    logger.debug("filtered out %s: %s", address, reason)
                    continue

                # Signal
                signal = calculate_signal(analysis)

                # Post
                text = format_new_token_post(analysis, signal)
                await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)

                # Persiste
                await self.storage.save_posted(analysis, signal)

                # Stats
                self.today_stats["posted"] += 1
                if signal == "BUY":
                    self.today_stats["buy"] += 1
                elif signal == "WATCH":
                    self.today_stats["watch"] += 1
                elif signal == "AVOID":
                    self.today_stats["avoid"] += 1

                self.today_tokens.append({
                    "symbol": analysis.get("symbol"),
                    "signal": signal,
                })

                posted += 1
                logger.info("Radar: posted %s (%s)", analysis.get("symbol"), signal)

                # Petite pause anti-spam entre 2 posts
                await asyncio.sleep(2)

            except Exception as exc:
                logger.error("Radar: post failed for %s: %s", pool.get("address"), exc)
                continue

        logger.info("Radar: scan done, posted %d", posted)
        return {"posted": posted, "errors": 0}

    # ------------------------------------------------------------------
    # Job 2 : updates 6h / 24h (toutes les heures)
    # ------------------------------------------------------------------
    async def send_updates(self) -> None:
        """Envoie les updates 6h et 24h pour les tokens déjà postés."""
        for hours in (6, 24):
            try:
                tokens = await self.storage.list_for_update(hours_ago=float(hours))
            except Exception as exc:
                logger.error("Radar: list_for_update failed: %s", exc)
                continue

            for token in tokens:
                if hours == 6 and token.get("update_6h_sent"):
                    continue
                if hours == 24 and token.get("update_24h_sent"):
                    continue

                try:
                    address = token.get("contract_address")
                    chain = token.get("chain")
                    if not address:
                        continue

                    current = await self.analyzer.analyze(address, chain_hint=chain)
                    text = format_update_post(token, current, hours)
                    if not text:
                        continue

                    await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
                    await self.storage.mark_update_sent(token["id"], hours)

                    logger.info("Radar: update %dh sent for %s", hours, token.get("symbol"))
                    await asyncio.sleep(2)

                except Exception as exc:
                    logger.error("Radar: update failed for %s: %s", token.get("id"), exc)

    # ------------------------------------------------------------------
    # Job 3 : tip du jour (une fois par jour)
    # ------------------------------------------------------------------
    async def send_tip(self) -> None:
        try:
            text = format_tip_of_the_day()
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
        except Exception as exc:
            logger.error("Radar: tip failed: %s", exc)

    # ------------------------------------------------------------------
    # Job 4 : récap quotidien (fin de journée)
    # ------------------------------------------------------------------
    async def send_daily_recap(self) -> None:
        try:
            text = format_daily_recap(self.today_tokens, self.today_stats)
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
            # Reset pour le lendemain
            self.today_tokens = []
            self.today_stats = {"scanned": 0, "posted": 0, "buy": 0, "watch": 0, "avoid": 0}
        except Exception as exc:
            logger.error("Radar: daily recap failed: %s", exc)

    # ------------------------------------------------------------------
    # Job 5 : stats du matin (bilan de la veille)
    # ------------------------------------------------------------------
    async def send_daily_stats(self) -> None:
        try:
            text = format_daily_stats(self.today_stats)
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
        except Exception as exc:
            logger.error("Radar: daily stats failed: %s", exc)

    # ------------------------------------------------------------------
    # Démarrage
    # ------------------------------------------------------------------
    def start_scheduler(self) -> None:
        if self.scheduler.running:
            return

        # Scan toutes les 15 min
        self.scheduler.add_job(
            self.scan_and_post,
            "interval",
            minutes=15,
            id="radar_scan",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        # Updates toutes les heures
        self.scheduler.add_job(
            self.send_updates,
            "interval",
            hours=1,
            id="radar_updates",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        # Tip quotidien à 15:00 UTC
        self.scheduler.add_job(
            self.send_tip,
            "cron",
            hour=15,
            minute=0,
            id="radar_tip",
            replace_existing=True,
        )

        # Recap quotidien à 20:00 UTC
        self.scheduler.add_job(
            self.send_daily_recap,
            "cron",
            hour=20,
            minute=0,
            id="radar_recap",
            replace_existing=True,
        )

        # Stats du matin à 08:00 UTC
        self.scheduler.add_job(
            self.send_daily_stats,
            "cron",
            hour=8,
            minute=0,
            id="radar_stats",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Radar: scheduler started (5 jobs)")

    async def close(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        await self.bot.session.close()
