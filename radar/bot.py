"""Radar bot — scans, filters, posts to the Telegram channel."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from analysis.token_analyzer import TokenAnalyzer
from config import Settings
from radar.filter import apply_filters, calculate_signal
from radar.formatter import (
    build_sniper_keyboard, format_daily_recap, format_daily_stats,
    format_new_token_post, format_pump_alert, format_tip_of_the_day,
)
from radar.scanner import RadarScanner
from radar.storage import RadarStorage

logger = logging.getLogger(__name__)

class RadarBot:
    def __init__(self, settings: Settings, analyzer: TokenAnalyzer, bot_token: str, channel_id: str) -> None:
        self.settings = settings
        self.analyzer = analyzer
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.bot = Bot(bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.scanner = RadarScanner()
        self.storage = RadarStorage(settings.supabase_url, settings.supabase_anon_key)
        self.scheduler = AsyncIOScheduler()

        try:
            from radar.sniper import set_jupiter_key
            jupiter_key = os.getenv("JUPITER_REFERRAL_KEY")
            set_jupiter_key(jupiter_key)
        except Exception:
            pass

        self.today_stats = {"scanned": 0, "posted": 0, "buy": 0, "watch": 0, "avoid": 0}
        self.today_tokens: list[dict[str, Any]] = []

    async def scan_and_post(self) -> dict[str, int]:
        logger.info("Radar: scan started")
        try:
            pools = await self.scanner.fetch_all_sources(limit_per_source=25)
        except Exception as exc:
            logger.error("Radar: scanner failed: %s", exc)
            return {"posted": 0, "errors": 1}

        posted = 0
        self.today_stats["scanned"] += len(pools)

        for pool in pools:
            try:
                address = pool.get("address")
                chain = pool.get("chain")
                if not address or not chain or await self.storage.already_posted(address, chain):
                    continue

                if chain == "solana":
                    analysis = dict(pool)
                    analysis["risk"] = {"score": None, "factors": {}} 
                    analysis["holder_count"] = None
                    analysis["top10_holder_pct"] = None
                    analysis["is_honeypot"] = False
                else:
                    analysis = await self.analyzer.analyze(address, chain_hint=chain)

                for k in ("price_change_h1", "price_change_h6", "price_change_h24", "image_uri", "twitter_url", "website_url"):
                    if pool.get(k) is not None and not analysis.get(k):
                        analysis[k] = pool[k]
                if pool.get("pair_created_at") and not analysis.get("pair_created_at"):
                    analysis["pair_created_at"] = pool.get("pair_created_at")

                passed, reason = apply_filters(analysis)
                if not passed:
                    continue

                signal = calculate_signal(analysis)
                text = format_new_token_post(analysis, signal)
                keyboard = build_sniper_keyboard(analysis)
                
                await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True, reply_markup=keyboard)
                await self.storage.save_posted(analysis, signal)

                self.today_stats["posted"] += 1
                self.today_tokens.append({"symbol": analysis.get("symbol"), "signal": signal})
                posted += 1
                await asyncio.sleep(2)
            except Exception as exc:
                logger.error("Radar: post failed for %s: %s", pool.get("address"), exc)

        logger.info("Radar: scan done, posted %d", posted)
        return {"posted": posted, "errors": 0}

    async def check_pumps(self) -> None:
        """Vérifie si les tokens postés ont atteint un nouveau palier."""
        logger.info("Radar: checking for pumps...")
        MILESTONES = [2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0]

        try:
            tokens = await self.storage.list_for_update(hours_ago=48.0)
        except Exception as exc:
            logger.error("Radar: list_for_update failed: %s", exc)
            return

        for token in tokens:
            try:
                address = token.get("contract_address")
                chain = token.get("chain")
                if not address:
                    continue

                if chain == "solana":
                    current = await self.analyzer.get_market_snapshot(address, chain_hint=chain)
                else:
                    current = await self.analyzer.analyze(address, chain_hint=chain)

                initial_mcap = token.get("initial_market_cap") or token.get("market_cap_usd")
                current_mcap = current.get("market_cap_usd")
                last_alert = token.get("last_alert_multiplier") or 1.0

                if not initial_mcap or not current_mcap or initial_mcap <= 0:
                    continue

                current_multiplier = current_mcap / initial_mcap

                highest_milestone_reached = 1.0
                for milestone in MILESTONES:
                    if current_multiplier >= milestone:
                        highest_milestone_reached = milestone
                    else:
                        break

                if highest_milestone_reached > last_alert:
                    text = format_pump_alert(token, current, highest_milestone_reached)
                    if text:
                        await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
                        await self.storage.update_last_multiplier(token["id"], highest_milestone_reached)
                        logger.info("Radar: Pump alert x%s sent for %s", highest_milestone_reached, token.get("symbol"))
                        await asyncio.sleep(2)

            except Exception as exc:
                logger.error("Radar: pump check failed for %s: %s", token.get("id"), exc)

    async def send_tip(self) -> None:
        try:
            text = format_tip_of_the_day()
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
        except Exception: pass

    async def send_daily_recap(self) -> None:
        try:
            text = format_daily_recap(self.today_tokens, self.today_stats)
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
            self.today_tokens = []
            self.today_stats = {"scanned": 0, "posted": 0, "buy": 0, "watch": 0, "avoid": 0}
        except Exception: pass

    async def send_daily_stats(self) -> None:
        try:
            text = format_daily_stats(self.today_stats)
            await self.bot.send_message(self.channel_id, text, disable_web_page_preview=True)
        except Exception: pass

    def start_scheduler(self) -> None:
        if self.scheduler.running: return
        
        self.scheduler.add_job(self.scan_and_post, "interval", minutes=15, id="radar_scan", max_instances=1, coalesce=True)
        self.scheduler.add_job(self.check_pumps, "interval", minutes=60, id="radar_pumps", max_instances=1, coalesce=True)
        self.scheduler.add_job(self.send_tip, "cron", hour=15, minute=0)
        self.scheduler.add_job(self.send_daily_recap, "cron", hour=20, minute=0)
        self.scheduler.add_job(self.send_daily_stats, "cron", hour=8, minute=0)
        self.scheduler.start()

    async def close(self) -> None:
        if self.scheduler.running: self.scheduler.shutdown(wait=False)
        await self.bot.session.close()
