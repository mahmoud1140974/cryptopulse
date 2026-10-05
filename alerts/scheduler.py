"""APScheduler integration for CryptoPulse alerts."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from alerts.alert_engine import AlertEngine
from config import Settings


class AlertScheduler:
    def __init__(self, settings: Settings, engine: AlertEngine) -> None:
        self.settings = settings
        self.engine = engine
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.scheduler.add_job(
            self.engine.check_once,
            "interval",
            minutes=self.settings.free_alert_interval_minutes,
            id="free_watchlist_alerts",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
