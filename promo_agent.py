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
            "The silent killers of memecoin portfolios: Honeypots.",
            "Why you should NEVER buy a token without checking if the Liquidity is locked.",
            "The Top 10 Holders trick: How whales dump on retail traders.",
            "Freeze Authority on Solana: The hidden switch that can lock your tokens.",
            "Stop trusting the hype. How to instantly verify if a contract is safe.",
            "A step-by-step mini-guide on how to scan a token before aping in.",
            "Why 90% of new memecoins fail, and how to find the 10% that survive.",
            "The anatomy of a Rug Pull: What are the warning signs?",
            "Don't get left holding the bag. Check the risk score before you buy."
        ]

    async def generate_post(self):
        if not self.gemini_key:
            logger.error("PromoAgent: GEMINI_API_KEY missing.")
            return None

        topic = random.choice(self.topics)
        prompt = (
            "You are an elite crypto security analyst. "
            "Write a highly engaging, scroll-stopping Telegram/Discord post.\n"
            "TOPIC: " + topic + "\n"
            "STRUCTURE: 1. HOOK (shocking statement) 2. VALUE (how CryptoPulse solves it) 3. CTA.\n"
            "RULES: Max 400 characters. 3 emojis. No hashtags. "
            "End with: 'Try it free now -> @CryptoPulse113_bot'"
        )

        # ✅ SOLUTION FIABLE : Alias 'gemini-flash-latest' sur l'endpoint stable 'v1'
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-flash-latest:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.gemini_key
        }
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"PromoAgent Gemini error (Code {response.status_code}): {response.text}")
                    return None
                
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
        except Exception as exc:
            logger.error(f"PromoAgent network error: {str(exc)}")
            return None

    async def send_discord(self, text):
        if not self.discord_webhook:
            return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.discord_webhook, json={"content": text})
                logger.info("PromoAgent: Sent to Discord.")
        except Exception as exc:
            logger.error(f"PromoAgent Discord error: {str(exc)}")

    async def send_telegram(self, text):
        if not self.telegram_token or not self.telegram_channel:
            return
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.telegram_channel, "text": text, "disable_web_page_preview": True}
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload)
                logger.info("PromoAgent: Sent to Telegram.")
        except Exception as exc:
            logger.error(f"PromoAgent Telegram error: {str(exc)}")

    async def run_cycle(self):
        logger.info("PromoAgent: Generating post...")
        text = await self.generate_post()
        if text:
            logger.info(f"PromoAgent generated: {text[:60]}...")
            await self.send_discord(text)
            await self.send_telegram(text)
        else:
            logger.warning("PromoAgent: No text generated, skipping sending.")

    def start_scheduler(self):
        if self.scheduler.running:
            return
        self.scheduler.add_job(self.run_cycle, "interval", minutes=60, id="promo_agent")
        self.scheduler.start()
        asyncio.create_task(self.run_cycle())

    async def close(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
