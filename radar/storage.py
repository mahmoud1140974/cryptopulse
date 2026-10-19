"""Radar storage — persists posted tokens in Supabase, prevents duplicates."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from supabase import create_client
except Exception:
    create_client = None

logger = logging.getLogger(__name__)


class RadarStorage:
    def __init__(self, supabase_url: str | None, supabase_key: str | None) -> None:
        self.supabase = None
        if supabase_url and supabase_key and create_client:
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("Radar storage: Supabase connected")
        else:
            logger.warning("Radar storage: Supabase NOT configured")

    @property
    def enabled(self) -> bool:
        return self.supabase is not None

    async def already_posted(self, address: str, chain: str) -> bool:
        if not self.supabase:
            return False
        addr = str(address or "").lower()
        chain_key = str(chain or "").lower()

        def run() -> bool:
            try:
                response = (
                    self.supabase.table("radar_tokens")
                    .select("id")
                    .eq("contract_address", addr)
                    .eq("chain", chain_key)
                    .limit(1)
                    .execute()
                )
                return bool(response.data)
            except Exception as exc:
                logger.warning("already_posted check failed: %s", exc)
                return False
        return await asyncio.to_thread(run)

    async def save_posted(self, analysis: dict[str, Any], signal: str) -> None:
        if not self.supabase:
            return
        addr = str(analysis.get("address") or "").lower()
        chain = str(analysis.get("chain") or "unknown").lower()
        risk = (analysis.get("risk") or {}).get("score")

        payload = {
            "contract_address": addr,
            "chain": chain,
            "symbol": analysis.get("symbol"),
            "name": analysis.get("name"),
            "risk_score": risk,
            "signal": signal,
            "liquidity_usd": analysis.get("liquidity_usd"),
            "holders": analysis.get("holder_count"),
            "initial_price": analysis.get("price_usd"),
            "initial_liquidity": analysis.get("liquidity_usd"),
            "initial_market_cap": analysis.get("market_cap_usd"), # ✅ AJOUTÉ ICI
            "last_alert_multiplier": 1.0, # ✅ AJOUTÉ ICI (par défaut à 1)
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }

        def run() -> None:
            try:
                self.supabase.table("radar_tokens").insert(payload).execute()
            except Exception as exc:
                logger.error("save_posted failed for %s: %s", addr, exc)
        await asyncio.to_thread(run)

    async def count_today(self) -> int:
        """Compte combien de tokens ont été postés aujourd'hui."""
        if not self.supabase:
            return 0
        today = datetime.now(timezone.utc).date().isoformat()

        def run() -> int:
            try:
                response = (
                    self.supabase.table("radar_tokens")
                    .select("id", count="exact")
                    .gte("posted_at", today)
                    .execute()
                )
                return response.count or 0
            except Exception as exc:
                logger.warning("count_today failed: %s", exc)
                return 0
        return await asyncio.to_thread(run)

    async def list_for_update(self, hours_ago: float) -> list[dict[str, Any]]:
        """
        Renvoie TOUS les tokens postés depuis X heures (ex: 48h).
        """
        if not self.supabase:
            return []

        now = datetime.now(timezone.utc)
        window_start = (now - timedelta(hours=hours_ago)).isoformat()

        def run() -> list[dict[str, Any]]:
            try:
                response = (
                    self.supabase.table("radar_tokens")
                    .select("*")
                    .gte("posted_at", window_start)
                    .execute()
                )
                return response.data or []
            except Exception as exc:
                logger.warning("list_for_update failed: %s", exc)
                return []
        return await asyncio.to_thread(run)

    async def mark_update_sent(self, token_id: str, hours: int) -> None:
        """Marque 'update_6h_sent' ou 'update_24h_sent' à True."""
        if not self.supabase:
            return
        if hours == 6:
            payload = {"update_6h_sent": True}
        elif hours == 24:
            payload = {"update_24h_sent": True}
        else:
            return

        def run() -> None:
            try:
                self.supabase.table("radar_tokens").update(payload).eq("id", token_id).execute()
            except Exception as exc:
                logger.warning("mark_update_sent failed: %s", exc)
        await asyncio.to_thread(run)

    # ✅ NOUVELLE FONCTION POUR LES PALIERS
    async def update_last_multiplier(self, token_id: str, multiplier: float) -> None:
        """Met à jour le dernier multiplicateur d'alerte envoyé (x2, x3, x10...)."""
        if not self.supabase:
            return

        def run() -> None:
            try:
                self.supabase.table("radar_tokens").update(
                    {"last_alert_multiplier": multiplier}
                ).eq("id", token_id).execute()
            except Exception as exc:
                logger.warning("update_last_multiplier failed for %s: %s", token_id, exc)
        
        await asyncio.to_thread(run)
