"""
DISHA Supabase Client.
Provides async-safe Supabase client singletons.
"""

from __future__ import annotations

from typing import Any, Optional

from supabase import Client, create_client

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("db")

_supabase_client: Optional[Client] = None
_supabase_admin: Optional[Client] = None


def get_supabase(settings: Optional[Settings] = None) -> Client:
    """
    Get a Supabase client using the anon key.
    Used for public/authenticated requests (respects RLS).
    """
    global _supabase_client
    if _supabase_client is None:
        s = settings or get_settings()
        if not s.has_supabase:
            logger.warning("supabase_not_configured", hint="Using demo mode — no database")
            raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        _supabase_client = create_client(s.supabase_url, s.supabase_anon_key)
        logger.info("supabase_client_created", url=s.supabase_url)
    return _supabase_client


def get_supabase_admin(settings: Optional[Settings] = None) -> Client:
    """
    Get a Supabase client using the service-role key.
    Bypasses RLS — use ONLY for admin/ingestion operations.
    """
    global _supabase_admin
    if _supabase_admin is None:
        s = settings or get_settings()
        if not s.supabase_service_role_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is required for admin operations.")
        _supabase_admin = create_client(s.supabase_url, s.supabase_service_role_key)
        logger.info("supabase_admin_client_created")
    return _supabase_admin


class SupabaseDB:
    """
    Thin wrapper around Supabase client for common DB operations.
    Keeps query logic DRY and testable.
    """

    def __init__(self, admin: bool = False):
        self._admin = admin

    @property
    def client(self) -> Client:
        return get_supabase_admin() if self._admin else get_supabase()

    def table(self, name: str):
        return self.client.table(name)

    # --- Generic CRUD helpers ---

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[dict]:
        """Select rows with optional filters, ordering, pagination."""
        query = self.client.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    query = query.in_(key, value)
                else:
                    query = query.eq(key, value)

        if order_by:
            desc = order_by.startswith("-")
            col = order_by.lstrip("-")
            query = query.order(col, desc=desc)

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.range(offset, offset + (limit or 20) - 1)

        result = query.execute()
        return result.data or []

    def select_one(self, table: str, id: str, columns: str = "*") -> Optional[dict]:
        """Select a single row by id."""
        result = self.client.table(table).select(columns).eq("id", id).limit(1).execute()
        return result.data[0] if result.data else None

    def insert(self, table: str, data: dict | list[dict]) -> list[dict]:
        """Insert one or more rows."""
        result = self.client.table(table).insert(data).execute()
        return result.data or []

    def update(self, table: str, id: str, data: dict) -> Optional[dict]:
        """Update a row by id."""
        result = self.client.table(table).update(data).eq("id", id).execute()
        return result.data[0] if result.data else None

    def upsert(self, table: str, data: dict | list[dict]) -> list[dict]:
        """Upsert one or more rows."""
        result = self.client.table(table).upsert(data).execute()
        return result.data or []

    def delete(self, table: str, id: str) -> bool:
        """Delete a row by id."""
        result = self.client.table(table).delete().eq("id", id).execute()
        return bool(result.data)

    def rpc(self, function_name: str, params: Optional[dict] = None) -> Any:
        """Call a Supabase RPC (database function)."""
        return self.client.rpc(function_name, params or {}).execute()


# Convenience singletons
db = SupabaseDB(admin=False)
db_admin = SupabaseDB(admin=True)
