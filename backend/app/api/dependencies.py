"""
DISHA API Dependencies.
FastAPI dependency injection for auth, DB, rate limiting.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.security import get_current_user, get_current_user_id, get_optional_user


async def get_demo_user(request: Request) -> dict[str, Any]:
    """
    For demo/hackathon: return the demo user profile.
    In production, this would verify the JWT and fetch from DB.
    """
    from app.services.seed_data import DEMO_STUDENT_PROFILE
    return DEMO_STUDENT_PROFILE


async def get_user_id_or_demo(request: Request) -> str:
    """
    For demo/hackathon: return demo user ID.
    Falls back to demo if no auth header is present.
    """
    auth = request.headers.get("authorization")
    if auth:
        try:
            settings = get_settings()
            from app.core.security import decode_supabase_token
            token = auth.replace("Bearer ", "")
            payload = decode_supabase_token(token, settings)
            return payload.get("sub", "demo-user-001")
        except Exception:
            pass
    return "demo-user-001"
