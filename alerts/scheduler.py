"""APScheduler integration for CryptoPulse alerts."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from alerts.alert_engine import AlertEngine
from config import Settings
from database.models import Database

logger = logging.getLogger(__name__)


class AlertScheduler:
    def __init__(self, settings: Settings, engine: AlertEngine, db: Database | None = None) -> None:
        self.settings = settings
        self.engine = engine
        self.db = db or engine.database if hasattr(engine, "database") else None
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if self.scheduler.running:
            return

        # Job 1 : vérification des mouvements de prix / liquidité
        self.scheduler.add_job(
            self.engine.check_once,
            "interval",
            minutes=self.settings.free_alert_interval_minutes,
            id="free_watchlist_alerts",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        # Job 2 : expiration des abonnements (toutes les 30 min)
        if self.db is not None:
            self.scheduler.add_job(
                self.expire_subscriptions,
                "interval",
                minutes=30,
                id="expire_subscriptions",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )

        self.scheduler.start()

    async def expire_subscriptions(self) -> dict[str, int]:
        """
        Rétrograde en Free tous les utilisateurs dont premium_until est dépassée.
        Ne crash jamais : log les erreurs et continue.
        """
        if self.db is None:
            return {"expired": 0, "errors": 0}

        expired = 0
        errors = 0
        try:
            users = await self.db.list_expired_premium_users()
        except Exception as exc:
            logger.error("expire_subscriptions list failed: %s", exc)
            return {"expired": 0, "errors": 1}

        for user in users:
            try:
                tid = user.get("telegram_id")
                if tid is None:
                    continue
                await self.db.downgrade_to_free(int(tid))
                expired += 1
                logger.info("Subscription expired for user %s (was %s)", tid, user.get("plan"))
                # Notification optionnelle
                if getattr(self.engine, "bot", None) is not None:
                    try:
                        await self.engine.bot.send_message(
                            int(tid),
                            "⏰ <b>Your CryptoPulse subscription has expired.</b>\n\n"
                            "Your account has been downgraded to the Free plan.\n\n"
                            "Use /subscribe to renew and get back your premium features.",
                            parse_mode="HTML",
                        )
                    except Exception as notify_exc:
                        logger.warning("Failed to notify user %s: %s", tid, notify_exc)
            except Exception as exc:
                errors += 1
                logger.error("Failed to expire subscription for %s: %s", user.get("telegram_id"), exc)

        logger.info("Subscription expiry job: %d expired, %d errors", expired, errors)
        return {"expired": expired, "errors": errors}

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
