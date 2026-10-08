"""Database access layer for SQLite development and Supabase production."""

from __future__ import annotations

import asyncio
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import Settings

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.backend = "supabase" if settings.supabase_configured else "sqlite"
        self.sqlite_path = settings.sqlite_path
        self.supabase = None
        if self.backend == "supabase" and create_client:
            self.supabase = create_client(settings.supabase_url, settings.supabase_anon_key)

    async def init_schema(self) -> None:
        if self.backend == "sqlite":
            await asyncio.to_thread(self._init_sqlite_schema)

    def _connect(self) -> sqlite3.Connection:
        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _ensure_column(conn: sqlite3.Connection, table: str, column: str, coltype: str = "TEXT") -> None:
        """Ajoute une colonne si elle n'existe pas (migration SQLite)."""
        try:
            cur = conn.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cur.fetchall()]
            if column not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        except Exception:
            pass

    def _init_sqlite_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    plan TEXT NOT NULL DEFAULT 'free',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    telegram_id INTEGER NOT NULL,
                    chain TEXT NOT NULL,
                    contract_address TEXT NOT NULL,
                    risk_score INTEGER,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS watchlist (
                    id TEXT PRIMARY KEY,
                    telegram_id INTEGER NOT NULL,
                    chain TEXT NOT NULL,
                    contract_address TEXT NOT NULL,
                    symbol TEXT,
                    name TEXT,
                    last_price REAL,
                    last_liquidity REAL,
                    last_volume REAL,
                    avg_volume REAL,
                    created_at TEXT NOT NULL,
                    UNIQUE(telegram_id, chain, contract_address)
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    telegram_id INTEGER NOT NULL,
                    watchlist_id TEXT,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tracked_wallets (
                    id TEXT PRIMARY KEY,
                    telegram_id INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    chain TEXT NOT NULL DEFAULT 'ethereum',
                    label TEXT,
                    last_tx_hash TEXT,
                    last_tx_time TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(telegram_id, address, chain)
                );
                """
            )
            self._ensure_column(conn, "users", "premium_until", "TEXT")

    # ------------------------------------------------------------------
    # Helpers SQLite
    # ------------------------------------------------------------------
    async def _sqlite_fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        def run() -> list[dict[str, Any]]:
            with self._connect() as conn:
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]
        return await asyncio.to_thread(run)

    async def _sqlite_fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = await self._sqlite_fetchall(query, params)
        return rows[0] if rows else None

    async def _sqlite_execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        def run() -> None:
            with self._connect() as conn:
                conn.execute(query, params)
        await asyncio.to_thread(run)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    async def get_or_create_user(self, telegram_id: int) -> dict[str, Any]:
        if self.backend == "supabase":
            return await self._supabase_get_or_create_user(telegram_id)
        existing = await self._sqlite_fetchone("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        if existing:
            return existing
        row = {"telegram_id": telegram_id, "plan": "free", "created_at": utc_now()}
        await self._sqlite_execute(
            "INSERT INTO users (telegram_id, plan, created_at) VALUES (?, ?, ?)",
            (telegram_id, "free", row["created_at"]),
        )
        return row

    async def _supabase_get_or_create_user(self, telegram_id: int) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            response = self.supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
            if response.data:
                return response.data[0]
            payload = {"telegram_id": telegram_id, "plan": "free", "created_at": utc_now()}
            inserted = self.supabase.table("users").insert(payload).execute()
            return inserted.data[0] if inserted.data else payload
        return await asyncio.to_thread(run)

    async def set_user_plan(
        self,
        telegram_id: int,
        plan: str,
        premium_until: str | None = None,
    ) -> None:
        if self.backend == "supabase":
            def run() -> None:
                self.supabase.table("users").update({
                    "plan": plan,
                    "premium_until": premium_until,
                }).eq("telegram_id", telegram_id).execute()
            await asyncio.to_thread(run)
            return
        await self.get_or_create_user(telegram_id)
        await self._sqlite_execute(
            "UPDATE users SET plan = ?, premium_until = ? WHERE telegram_id = ?",
            (plan, premium_until, telegram_id),
        )

    async def list_expired_premium_users(self) -> list[dict[str, Any]]:
        now_iso = datetime.now(timezone.utc).isoformat()
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = (
                    self.supabase.table("users")
                    .select("*")
                    .neq("plan", "free")
                    .lt("premium_until", now_iso)
                    .execute()
                )
                return [r for r in (response.data or []) if r.get("premium_until")]
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall(
            """
            SELECT * FROM users
            WHERE plan != 'free'
              AND premium_until IS NOT NULL
              AND premium_until < ?
            """,
            (now_iso,),
        )

    async def downgrade_to_free(self, telegram_id: int) -> None:
        await self.set_user_plan(telegram_id, "free", None)

    # ------------------------------------------------------------------
    # Scans
    # ------------------------------------------------------------------
    async def record_scan(self, telegram_id: int, chain: str, contract_address: str, risk_score: int | None) -> None:
        row = {
            "id": str(uuid.uuid4()),
            "telegram_id": telegram_id,
            "chain": chain,
            "contract_address": contract_address,
            "risk_score": risk_score,
            "created_at": utc_now(),
        }
        if self.backend == "supabase":
            await asyncio.to_thread(lambda: self.supabase.table("scans").insert(row).execute())
            return
        await self._sqlite_execute(
            "INSERT INTO scans (id, telegram_id, chain, contract_address, risk_score, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (row["id"], telegram_id, chain, contract_address, risk_score, row["created_at"]),
        )

    async def count_scans_today(self, telegram_id: int) -> int:
        today = datetime.now(timezone.utc).date().isoformat()
        if self.backend == "supabase":
            def run() -> int:
                response = (
                    self.supabase.table("scans")
                    .select("id", count="exact")
                    .eq("telegram_id", telegram_id)
                    .gte("created_at", today)
                    .execute()
                )
                return response.count or 0
            return await asyncio.to_thread(run)
        row = await self._sqlite_fetchone(
            "SELECT COUNT(*) AS count FROM scans WHERE telegram_id = ? AND created_at >= ?",
            (telegram_id, today),
        )
        return int(row["count"]) if row else 0

    async def count_scans_this_month(self, telegram_id: int) -> int:
        """Compte le nombre de scans pour le mois en cours (UTC)."""
        now = datetime.now(timezone.utc)
        first_of_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ).isoformat()

        if self.backend == "supabase":
            def run() -> int:
                response = (
                    self.supabase.table("scans")
                    .select("id", count="exact")
                    .eq("telegram_id", telegram_id)
                    .gte("created_at", first_of_month)
                    .execute()
                )
                return response.count or 0
            return await asyncio.to_thread(run)

        row = await self._sqlite_fetchone(
            "SELECT COUNT(*) AS count FROM scans WHERE telegram_id = ? AND created_at >= ?",
            (telegram_id, first_of_month),
        )
        return int(row["count"]) if row else 0

    # ------------------------------------------------------------------
    # Watchlist
    # ------------------------------------------------------------------
    async def add_watchlist(
        self,
        telegram_id: int,
        chain: str,
        contract_address: str,
        symbol: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        existing = await self._sqlite_fetchone(
            "SELECT * FROM watchlist WHERE telegram_id = ? AND chain = ? AND contract_address = ?",
            (telegram_id, chain, contract_address),
        ) if self.backend == "sqlite" else await self._supabase_find_watchlist(telegram_id, chain, contract_address)
        if existing:
            return existing

        row = {
            "id": str(uuid.uuid4()),
            "telegram_id": telegram_id,
            "chain": chain,
            "contract_address": contract_address,
            "symbol": symbol,
            "name": name,
            "created_at": utc_now(),
        }
        if self.backend == "supabase":
            await asyncio.to_thread(lambda: self.supabase.table("watchlist").insert(row).execute())
            return row
        await self._sqlite_execute(
            """
            INSERT INTO watchlist (id, telegram_id, chain, contract_address, symbol, name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (row["id"], telegram_id, chain, contract_address, symbol, name, row["created_at"]),
        )
        return row

    async def _supabase_find_watchlist(self, telegram_id: int, chain: str, contract_address: str) -> dict[str, Any] | None:
        def run() -> dict[str, Any] | None:
            response = (
                self.supabase.table("watchlist")
                .select("*")
                .eq("telegram_id", telegram_id)
                .eq("chain", chain)
                .eq("contract_address", contract_address)
                .execute()
            )
            return response.data[0] if response.data else None
        return await asyncio.to_thread(run)

    async def count_watchlist(self, telegram_id: int) -> int:
        if self.backend == "supabase":
            def run() -> int:
                response = self.supabase.table("watchlist").select("id", count="exact").eq("telegram_id", telegram_id).execute()
                return response.count or 0
            return await asyncio.to_thread(run)
        row = await self._sqlite_fetchone("SELECT COUNT(*) AS count FROM watchlist WHERE telegram_id = ?", (telegram_id,))
        return int(row["count"]) if row else 0

    async def list_watchlist(self, telegram_id: int, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = (
                    self.supabase.table("watchlist")
                    .select("*")
                    .eq("telegram_id", telegram_id)
                    .order("created_at", desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )
                return response.data or []
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall(
            "SELECT * FROM watchlist WHERE telegram_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (telegram_id, limit, offset),
        )

    async def list_all_watchlist(self) -> list[dict[str, Any]]:
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = self.supabase.table("watchlist").select("*").execute()
                return response.data or []
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall("SELECT * FROM watchlist")

    async def get_watchlist_item(self, item_id: str) -> dict[str, Any] | None:
        if self.backend == "supabase":
            def run() -> dict[str, Any] | None:
                response = self.supabase.table("watchlist").select("*").eq("id", item_id).execute()
                return response.data[0] if response.data else None
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchone("SELECT * FROM watchlist WHERE id = ?", (item_id,))

    async def remove_watchlist(self, telegram_id: int, item_id: str) -> None:
        if self.backend == "supabase":
            await asyncio.to_thread(
                lambda: self.supabase.table("watchlist").delete().eq("telegram_id", telegram_id).eq("id", item_id).execute()
            )
            return
        await self._sqlite_execute("DELETE FROM watchlist WHERE telegram_id = ? AND id = ?", (telegram_id, item_id))

    async def update_watchlist_snapshot(
        self,
        item_id: str,
        price: float | None,
        liquidity: float | None,
        volume: float | None,
        avg_volume: float | None,
    ) -> None:
        payload = {
            "last_price": price,
            "last_liquidity": liquidity,
            "last_volume": volume,
            "avg_volume": avg_volume,
        }
        if self.backend == "supabase":
            await asyncio.to_thread(lambda: self.supabase.table("watchlist").update(payload).eq("id", item_id).execute())
            return
        await self._sqlite_execute(
            "UPDATE watchlist SET last_price = ?, last_liquidity = ?, last_volume = ?, avg_volume = ? WHERE id = ?",
            (price, liquidity, volume, avg_volume, item_id),
        )

    # ------------------------------------------------------------------
    # Alerts
    # ------------------------------------------------------------------
    async def insert_alert(self, telegram_id: int, watchlist_id: str | None, alert_type: str, message: str) -> None:
        row = {
            "id": str(uuid.uuid4()),
            "telegram_id": telegram_id,
            "watchlist_id": watchlist_id,
            "alert_type": alert_type,
            "message": message,
            "created_at": utc_now(),
        }
        if self.backend == "supabase":
            await asyncio.to_thread(lambda: self.supabase.table("alerts").insert(row).execute())
            return
        await self._sqlite_execute(
            "INSERT INTO alerts (id, telegram_id, watchlist_id, alert_type, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (row["id"], telegram_id, watchlist_id, alert_type, message, row["created_at"]),
        )

    async def list_alerts(self, telegram_id: int, limit: int = 20) -> list[dict[str, Any]]:
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = (
                    self.supabase.table("alerts")
                    .select("*")
                    .eq("telegram_id", telegram_id)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                return response.data or []
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall(
            "SELECT * FROM alerts WHERE telegram_id = ? ORDER BY created_at DESC LIMIT ?",
            (telegram_id, limit),
        )

    # ------------------------------------------------------------------
    # Tracked wallets
    # ------------------------------------------------------------------
    async def add_tracked_wallet(
        self,
        telegram_id: int,
        address: str,
        chain: str = "ethereum",
        label: str | None = None,
    ) -> dict[str, Any]:
        existing = await self.get_tracked_wallet(telegram_id, address, chain)
        if existing:
            return existing

        row = {
            "id": str(uuid.uuid4()),
            "telegram_id": telegram_id,
            "address": address,
            "chain": chain,
            "label": label,
            "created_at": utc_now(),
        }
        if self.backend == "supabase":
            await asyncio.to_thread(
                lambda: self.supabase.table("tracked_wallets").insert(row).execute()
            )
            return row

        await self._sqlite_execute(
            """
            INSERT INTO tracked_wallets (id, telegram_id, address, chain, label, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (row["id"], telegram_id, address, chain, label, row["created_at"]),
        )
        return row

    async def get_tracked_wallet(
        self,
        telegram_id: int,
        address: str,
        chain: str = "ethereum",
    ) -> dict[str, Any] | None:
        if self.backend == "supabase":
            def run() -> dict[str, Any] | None:
                response = (
                    self.supabase.table("tracked_wallets")
                    .select("*")
                    .eq("telegram_id", telegram_id)
                    .eq("address", address)
                    .eq("chain", chain)
                    .execute()
                )
                return response.data[0] if response.data else None
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchone(
            "SELECT * FROM tracked_wallets WHERE telegram_id = ? AND address = ? AND chain = ?",
            (telegram_id, address, chain),
        )

    async def list_tracked_wallets(
        self,
        telegram_id: int,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = (
                    self.supabase.table("tracked_wallets")
                    .select("*")
                    .eq("telegram_id", telegram_id)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                return response.data or []
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall(
            "SELECT * FROM tracked_wallets WHERE telegram_id = ? ORDER BY created_at DESC LIMIT ?",
            (telegram_id, limit),
        )

    async def list_all_tracked_wallets(self) -> list[dict[str, Any]]:
        if self.backend == "supabase":
            def run() -> list[dict[str, Any]]:
                response = self.supabase.table("tracked_wallets").select("*").execute()
                return response.data or []
            return await asyncio.to_thread(run)
        return await self._sqlite_fetchall("SELECT * FROM tracked_wallets")

    async def count_tracked_wallets(self, telegram_id: int) -> int:
        if self.backend == "supabase":
            def run() -> int:
                response = (
                    self.supabase.table("tracked_wallets")
                    .select("id", count="exact")
                    .eq("telegram_id", telegram_id)
                    .execute()
                )
                return response.count or 0
            return await asyncio.to_thread(run)
        row = await self._sqlite_fetchone(
            "SELECT COUNT(*) AS count FROM tracked_wallets WHERE telegram_id = ?",
            (telegram_id,),
        )
        return int(row["count"]) if row else 0

    async def remove_tracked_wallet(
        self,
        telegram_id: int,
        address: str,
        chain: str = "ethereum",
    ) -> None:
        if self.backend == "supabase":
            await asyncio.to_thread(
                lambda: self.supabase.table("tracked_wallets")
                .delete()
                .eq("telegram_id", telegram_id)
                .eq("address", address)
                .eq("chain", chain)
                .execute()
            )
            return
        await self._sqlite_execute(
            "DELETE FROM tracked_wallets WHERE telegram_id = ? AND address = ? AND chain = ?",
            (telegram_id, address, chain),
        )

    async def update_wallet_snapshot(
        self,
        wallet_id: str,
        last_tx_hash: str | None,
        last_tx_time: str | None,
    ) -> None:
        payload = {
            "last_tx_hash": last_tx_hash,
            "last_tx_time": last_tx_time,
        }
        if self.backend == "supabase":
            await asyncio.to_thread(
                lambda: self.supabase.table("tracked_wallets")
                .update(payload)
                .eq("id", wallet_id)
                .execute()
            )
            return
        await self._sqlite_execute(
            "UPDATE tracked_wallets SET last_tx_hash = ?, last_tx_time = ? WHERE id = ?",
            (last_tx_hash, last_tx_time, wallet_id),
        )

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------
    async def log_error(self, message: str, level: str = "ERROR") -> None:
        safe_message = message[:1000]
        row = {"id": str(uuid.uuid4()), "level": level, "message": safe_message, "created_at": utc_now()}
        if self.backend == "supabase":
            await asyncio.to_thread(lambda: self.supabase.table("admin_logs").insert(row).execute())
            return
        await self._sqlite_execute(
            "INSERT INTO admin_logs (id, level, message, created_at) VALUES (?, ?, ?, ?)",
            (row["id"], level, safe_message, row["created_at"]),
        )
