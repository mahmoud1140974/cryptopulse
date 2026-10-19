"""Promo Agent — Uses Gemini AI to generate high-converting posts and sends them to Discord & Telegram."""

from __future__ import annotations

import asyncio
import logging
import os
import random
from datetime import datetime

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

class PromoAgent:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        # On réutilise les accès de ton bot Radar pour Telegram
        self.telegram_token = os.getenv("RADAR_BOT_TOKEN")
        self.telegram_channel = os.getenv("RADAR_CHANNEL_ID")
        self.scheduler = AsyncIOScheduler()
        
        # Sujets conçus pour susciter la curiosité, la peur de rater (FOMO) ou l'éducation
        self.topics = [
            "The silent killers of memecoin portfolios: Honeypots. Explain how to avoid them.",
            "Why you should NEVER buy a token without checking if the Liquidity is locked.",
            "The 'Top 10 Holders' trick: How whales dump on retail traders and how to spot it.",
            "Freeze Authority on Solana: The hidden switch that can lock your tokens forever.",
            "Stop trusting the hype. How to instantly verify if a contract is safe in 3 seconds.",
            "A step-by-step mini-guide on how to scan a token before aping in.",
            "Why 90% of new memecoins fail, and how to find the 10% that survive.",
            "The anatomy of a Rug Pull: What are the warning signs?",
            "Don't get left holding the bag. Check the risk score before you buy.",
            "The easiest way to check a token's security without reading smart contracts."
        ]

    async def generate_post(self) -> str | None:
        """Demande à Gemini de rédiger un post de promo ultra-engageant."""
        if not self.gemini_key:
            logger.error("PromoAgent: GEMINI_API_KEY missing.")
            return None

        topic = random.choice(self.topics)
        
        # PROMPT AVANCÉ : On donne une personnalité, une structure et des contraintes à l'IA
        prompt = (
            "You are an elite crypto security analyst and a master copywriter. "
            "Your goal is to write a highly engaging, scroll-stopping Telegram/Discord post that drives crypto traders to use our free bot.\n\n"
            f"TOPIC: {topic}\n\n"
            "STRUCTURE TO FOLLOW:\n"
            "1. HOOK: Start with a strong, controversial statement, a shocking statistic, or a direct question about losing money.\n"
            "2. VALUE: Explain how CryptoPulse solves this problem instantly (mention features like risk score, liquidity check, or holder concentration).\n"
            "3. CALL TO ACTION (CTA): Tell them exactly what to do next to save their portfolio.\n\n"
            "RULES:\n"
            "- Max 450 characters.\n"
            "- Use 3 to 4 relevant emojis (🚀, 🛡️, 🚨, 🐋, 📊).\n"
            "- Do not use hashtags.\n"
            "- Sound like an authoritative human expert, not a robot.\n"
            "- MUST end with: 'Try it free now 👉 @CryptoPulse113_bot'"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
        except Exception as exc:
            logger.error("PromoAgent: Gemini API error: %s", exc)
            return None

    async def send_discord(self, text: str) -> None:
        """Envoie le post sur Discord via le Webhook."""
        if not self.discord_webhook:
            logger.warning("PromoAgent: No Discord webhook configured.")
            return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.discord_webhook, json={"content": text})
                logger.info("PromoAgent: Post sent to Discord.")
        except Exception as exc:
            logger.error("PromoAgent: Discord send failed: %s", exc)

    async def send_telegram(self, text: str) -> None:
        """Envoie le post sur Telegram via le bot Radar."""
        if not self.telegram_token or not self.telegram_channel:
            logger.warning("PromoAgent: Telegram not configured.")
            return
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.telegram_channel, "text": text, "disable_web_page_preview": True}
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload)
                logger.info("PromoAgent: Post sent to Telegram.")
        except Exception as exc:
            logger.error("PromoAgent: Telegram send failed: %s", exc)

    async def run_cycle(self):
        """Génère un post et l'envoie sur toutes les plateformes."""
        logger.info("PromoAgent: Starting promotion cycle...")
        text = await self.generate_post()
        if not text:
            return

        await self.send_discord(text)
        await self.send_telegram(text)
        logger.info("PromoAgent: Cycle complete.")

    def start_scheduler(self):
        """Lance la promotion automatique toutes les 1 heure."""
        if self.scheduler.running:
            return
        
        self.scheduler.add_job(
            self.run_cycle,
            "interval",
            minutes=60, 
            id="promo_agent",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.start()
        logger.info("PromoAgent: Scheduler started (runs every 1 hour).")

    async def close(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
