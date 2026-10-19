"""Promo Agent — Uses Gemini AI to generate high-converting posts and sends them to Discord & Telegram."""

from __future__ import annotations

import asyncio
import logging
import os
import random

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

class PromoAgent:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.telegram_token = os.getenv("RADAR_BOT_TOKEN")
        self.telegram_channel = os.getenv("RADAR_CHANNEL_ID")
        self.scheduler = AsyncIOScheduler()
        
        self.topics = [
            "The silent killers of memecoin portfolios: Honeypots. Explain how to avoid them.",
            "Why you should NEVER buy a token without checking if the Liquidity is locked.",
            "The 'Top 10 Holders' trick: How whales dump on retail traders and how to spot it.",
            "Freeze Authority on Solana: The hidden switch that can lock your tokens forever.",
            "Stop trusting the hype. How to instantly verify if a contract is safe in 3 seconds.",
            "A step-by-step mini-guide on how to scan a token before aping in.",
            "Why 90% of new memecoins fail, and how to find the 10% that survive.",
            "The anatomy of a Rug Pull: What are the warning signs?",
            "Don't get left holding the bag. Check the risk score before you buy."
        ]

    async def generate_post(self) -> str | None:
        if not self.gemini_key:
            logger.error("🚨 PromoAgent ERREUR: La variable GEMINI_API_KEY est introuvable sur Render !")
            return None

        topic = random.choice(self.topics)
        prompt = (
            "You are an elite crypto security analyst and a master copywriter. "
            "Write a highly engaging, scroll-stopping Telegram/Discord post.\n\n"
            f"TOPIC: {topic}\n\n"
            "STRUCTURE: 1. HOOK (shocking statement) 2. VALUE (how CryptoPulse solves it) 3. CTA (use the bot).\n"
            "RULES: Max 450 characters. 3-4 emojis. No hashtags. End with: 'Try it free now 👉 @CryptoPulse113_bot'"
        )

        # ✅ MODIFICATION : On utilise gemini-2.0-flash qui est le modèle actuel et gratuit.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    logger.error(f"🚨 PromoAgent Gemini a refusé la requête (Code {response.status_code}): {response.text}")
                    return None
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
        except Exception as exc:
            logger.error("🚨 PromoAgent Erreur réseau avec Gemini: %s", exc)
            return None

    async def send_discord(self, text: str) -> None:
        if not self.discord_webhook:
            logger.error("🚨 PromoAgent ERREUR: La variable DISCORD_WEBHOOK_URL est introuvable !")
            return
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.discord_webhook, json={"content": text})
                if response.status_code not in (200, 204):
                    logger.error(f"🚨 PromoAgent Discord a échoué (Code {response.status_code}): {response.text}")
                else:
                    logger.info("✅ PromoAgent: Message envoyé sur Discord !")
        except Exception as exc:
            logger.error("🚨 PromoAgent Erreur d'envoi Discord: %s", exc)

    async def send_telegram(self, text: str) -> None:
        if not self.telegram_token or not self.telegram_channel:
            logger.warning("⚠️ PromoAgent: Variables Telegram manquantes, envoi ignoré.")
            return
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.telegram_channel, "text": text, "disable_web_page_preview": True}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    logger.error(f"🚨 PromoAgent Telegram a échoué: {response.text}")
                else:
                    logger.info("✅ PromoAgent: Message envoyé sur Telegram !")
        except Exception as exc:
            logger.error("🚨 PromoAgent Erreur d'envoi Telegram: %s", exc)

    async def run_cycle(self):
        logger.info("🤖 PromoAgent: Début de la génération du post...")
        text = await self.generate_post()
        if not text:
            return
        logger.info(f"📝 PromoAgent: Texte généré: {text[:50]}...")
        await self.send_discord(text)
        await self.send_telegram(text)

    def start_scheduler(self):
        if self.scheduler.running:
            return
        self.scheduler.add_job(self.run_cycle, "interval", minutes=60, id="promo_agent", replace_existing=True)
        self.scheduler.start()
        
        # Lancement immédiat
        asyncio.create_task(self.run_cycle())

    async def close(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
