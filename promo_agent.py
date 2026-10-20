import asyncio
import logging
import os
import random

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from twikit import Client

logger = logging.getLogger(__name__)

class PromoAgent:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.twitter_auth = os.getenv("TWITTER_AUTH_TOKEN")
        self.twitter_ct0 = os.getenv("TWITTER_CT0")
        self.scheduler = AsyncIOScheduler()
        
        # 🎯 METS TON LIEN ICI (celui de ton canal)
        self.bot_url = "https://t.me/CryptoPulse113_bot"
        self.channel_url = "https://t.me/apexcryptolabs1"  # <--- MODIFIE CETTE LIGNE SI TU CRÉES UN NOUVEAU LIEN

        self.topics_bot = [
            "The silent killers of memecoin portfolios: Honeypots.",
            "Why you should NEVER buy a token without checking if the Liquidity is locked.",
            "The Top 10 Holders trick: How whales dump on retail traders.",
            "Freeze Authority on Solana: The hidden switch that can lock your tokens.",
            "Stop trusting the hype. How to instantly verify if a contract is safe.",
            "A step-by-step mini-guide on how to scan a token before aping in."
        ]

        self.topics_channel = [
            "Want to catch the next 100x memecoin before it pumps? Join our free signals channel.",
            "Stop missing out on early gems. We scan 1000+ tokens daily and post the best ones for free.",
            "Why pay for alpha groups when our Telegram channel posts new Solana gems automatically?",
            "Get real-time alerts on new Pump.fun tokens before they explode. Join the Radar channel.",
            "Tired of rug pulls? We filter the scams and post only the safest new tokens in our channel."
        ]

    async def generate_text(self, prompt_type: str, topic: str) -> str | None:
        if not self.groq_key:
            return None

        if prompt_type == "bot":
            prompt = (
                "You are an elite crypto security analyst. Write a short, engaging tweet/post.\n"
                f"TOPIC: {topic}\n"
                f"RULES: Max 200 characters. 2 emojis. End with: 'Try it free -> {self.bot_url}'"
            )
        else:
            prompt = (
                "You are a crypto marketing expert. Write a short, FOMO-inducing tweet/post.\n"
                f"TOPIC: {topic}\n"
                f"RULES: Max 200 characters. 2 emojis. End with: 'Join now -> {self.channel_url}'"
            )

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7, "max_tokens": 2048, "reasoning_effort": "low"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200: return None
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    async def send_discord(self, text):
        if not self.discord_webhook: return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.discord_webhook, json={"content": text})
                logger.info("PromoAgent: Sent to Discord.")
        except Exception: pass

    async def send_twitter(self, text):
        if not self.twitter_auth or not self.twitter_ct0: return
        try:
            safe_text = text[:270] if len(text) > 270 else text
            client = Client(language='en-US')
            client.set_cookies({'auth_token': self.twitter_auth, 'ct0': self.twitter_ct0})
            await client.create_tweet(text=safe_text)
            logger.info("PromoAgent: Sent to Twitter.")
        except Exception as exc:
            logger.error(f"PromoAgent Twitter error: {str(exc)}")

    async def run_bot_cycle(self):
        text = await self.generate_text("bot", random.choice(self.topics_bot))
        if text:
            await self.send_discord(text)
            await self.send_twitter(text)

    async def run_channel_cycle(self):
        text = await self.generate_text("channel", random.choice(self.topics_channel))
        if text:
            await self.send_discord(text)
            await self.send_twitter(text)

    def start_scheduler(self):
        if self.scheduler.running: return
        self.scheduler.add_job(self.run_bot_cycle, "interval", minutes=30, id="promo_bot")
        self.scheduler.add_job(self.run_channel_cycle, "interval", minutes=60, id="promo_channel")
        self.scheduler.start()
        asyncio.create_task(self.run_bot_cycle())
        asyncio.create_task(self.run_channel_cycle())

    async def close(self):
        if self.scheduler.running: self.scheduler.shutdown(wait=False)
