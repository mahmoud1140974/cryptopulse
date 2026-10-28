import asyncio
import logging
import os
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

import httpx
import feedparser
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
        
        self.bot_url = "https://t.me/CryptoPulse113_bot"
        self.channel_url = "https://t.me/apexcryptolabs1" 

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

        # Flux RSS (on garde les mêmes)
        self.news_feeds = [
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://news.google.com/rss/search?q=cryptocurrency+OR+bitcoin+OR+solana+OR+ethereum&hl=en-US&gl=US&ceid=US:en"
        ]
        self.posted_news_titles = []

    async def generate_text(self, prompt: str) -> str | None:
        if not self.groq_key:
            return None
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
        except Exception as exc:
            logger.error(f"PromoAgent Groq error: {exc}")
            return None

    async def download_image(self, image_url: str) -> str | None:
        """Télécharge une image et renvoie le chemin local."""
        try:
            parsed = urlparse(image_url)
            if not parsed.scheme or not parsed.path:
                return None
            # On garde l'extension du fichier (jpg, png, webp)
            ext = os.path.splitext(parsed.path)[1] or ".jpg"
            filepath = f"/tmp/news_image{ext}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=15.0)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return filepath
        except Exception as exc:
            logger.error(f"PromoAgent: Image download failed: {exc}")
        return None

    async def send_twitter(self, text, image_path=None):
        if not self.twitter_auth or not self.twitter_ct0:
            return
        try:
            safe_text = text[:270] if len(text) > 270 else text
            client = Client(language='en-US')
            client.set_cookies({'auth_token': self.twitter_auth, 'ct0': self.twitter_ct0})
            
            media_ids = None
            if image_path and os.path.exists(image_path):
                try:
                    media_id = await client.upload_media(image_path)
                    media_ids = [media_id]
                except Exception as e:
                    logger.error(f"PromoAgent: Media upload failed: {e}")

            if media_ids:
                await client.create_tweet(text=safe_text, media_ids=media_ids)
            else:
                await client.create_tweet(text=safe_text)
                
            logger.info("PromoAgent: Sent to Twitter.")
        except Exception as exc:
            logger.error(f"PromoAgent Twitter error: {str(exc)}")

    async def send_discord(self, text):
        if not self.discord_webhook: return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.discord_webhook, json={"content": text})
                logger.info("PromoAgent: Sent to Discord.")
        except Exception: pass

    async def run_bot_cycle(self):
        logger.info("PromoAgent: Generating BOT promotion...")
        topic = random.choice(self.topics_bot)
        prompt = (
            "You are an elite crypto security analyst. Write a short, engaging tweet/post.\n"
            f"TOPIC: {topic}\n"
            f"RULES: Max 200 characters. 2 emojis. End with: 'Try it free -> {self.bot_url}'"
        )
        text = await self.generate_text(prompt)
        if text:
            await self.send_discord(text)
            await self.send_twitter(text)

    async def run_channel_cycle(self):
        logger.info("PromoAgent: Generating CHANNEL promotion...")
        topic = random.choice(self.topics_channel)
        prompt = (
            "You are a crypto marketing expert. Write a short, FOMO-inducing tweet/post.\n"
            f"TOPIC: {topic}\n"
            f"RULES: Max 200 characters. 2 emojis. End with: 'Join now -> {self.channel_url}'"
        )
        text = await self.generate_text(prompt)
        if text:
            await self.send_discord(text)
            await self.send_twitter(text)

    async def run_news_cycle(self):
        logger.info("PromoAgent: Checking Crypto News...")
        latest_news = None

        for url in self.news_feeds:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    entry = feed.entries[0]
                    if entry.title not in self.posted_news_titles:
                        published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        if datetime.now(timezone.utc) - published_time < timedelta(hours=2):
                            latest_news = entry
                            break
            except Exception:
                continue

        if not latest_news:
            logger.info("PromoAgent: No fresh news found.")
            return

        logger.info(f"PromoAgent: New found: {latest_news.title}")

        # 1. Extraire l'image (si disponible)
        image_url = None
        if hasattr(latest_news, 'enclosures') and latest_news.enclosures:
            image_url = latest_news.enclosures[0].get('href')
        elif hasattr(latest_news, 'media_content') and latest_news.media_content:
            image_url = latest_news.media_content[0].get('url')
            
        image_path = await self.download_image(image_url) if image_url else None

        # 2. Générer le texte avec l'IA
        prompt = (
            "You are a top Crypto News reporter. Write a short, urgent, and engaging tweet about this news.\n"
            f"HEADLINE: {latest_news.title}\n"
            f"CONTEXT: {latest_news.get('summary', '')[:300]}\n"
            "RULES: Max 200 characters. 2 emojis. No hashtags. End with: 'More alpha on our channel -> " + self.channel_url + "'"
        )
        
        text = await self.generate_text(prompt)
        if text:
            await self.send_discord(text)
            # On envoie le tweet AVEC l'image
            await self.send_twitter(text, image_path=image_path)
            
            # Nettoyage de l'image temporaire
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            self.posted_news_titles.append(latest_news.title)
            if len(self.posted_news_titles) > 50: 
                self.posted_news_titles.pop(0)

    def start_scheduler(self):
        if self.scheduler.running: return
        
        self.scheduler.add_job(self.run_bot_cycle, "interval", minutes=30, id="promo_bot")
        self.scheduler.add_job(self.run_channel_cycle, "interval", minutes=60, id="promo_channel")
        self.scheduler.add_job(self.run_news_cycle, "interval", minutes=20, id="news_cycle")
        
        self.scheduler.start()
        
        asyncio.create_task(self.run_bot_cycle())
        asyncio.create_task(self.run_channel_cycle())
        asyncio.create_task(self.run_news_cycle())

    async def close(self):
        if self.scheduler.running: self.scheduler.shutdown(wait=False)
