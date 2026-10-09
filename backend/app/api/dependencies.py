"""
DISHA API Dependencies.
FastAPI dependency injection for auth, DB, rate limiting.

Auth Strategy:
- If Supabase is configured AND a Bearer token is present → verify token, use real user
- If Supabase is not configured OR no token → demo mode (for hackathon demo)
- Protected routes that REQUIRE auth call `require_auth_user`
- Public/demo routes use `get_demo_user` (always works)
"""

from __future__ import annotations

import copy
from typing import Any, Optional

from fastapi import Depends, Header, HTTPException, Request

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("dependencies")

# In-memory user profile store (keyed by user_id, used in demo mode)
_user_profiles: dict[str, dict] = {}


def _get_demo_profile() -> dict[str, Any]:
    from app.services.seed_data import DEMO_STUDENT_PROFILE
    return copy.deepcopy(DEMO_STUDENT_PROFILE)


async def get_demo_user(request: Request) -> dict[str, Any]:
    """
    Flexible auth dependency:
    1. If valid Supabase Bearer token → decode it, return user from in-memory store.
    2. Otherwise → return demo profile (safe for hackathon demo without Supabase).
    """
    settings = get_settings()
    auth = request.headers.get("authorization", "")

    if auth and settings.has_supabase:
        try:
            from app.core.security import decode_supabase_token
            token = auth.replace("Bearer ", "").strip()
            if token:
                payload = decode_supabase_token(token, settings)
                user_id = payload.get("sub", "demo-user-001")
                email = payload.get("email", "")

                # Return stored profile if it exists, else build one from JWT claims
                if user_id in _user_profiles:
                    return _user_profiles[user_id]

                # First-time user: create a minimal profile from token
                profile = _get_demo_profile()
                profile["user_id"] = user_id
                profile["email"] = email
                # Use email prefix as display name if not set
                if email and not profile.get("display_name"):
                    profile["display_name"] = email.split("@")[0].replace(".", " ").title()
                _user_profiles[user_id] = profile
                return profile
        except Exception as exc:
            logger.warning("token_decode_failed_using_demo", error=str(exc))

    # Demo mode fallback
    return _get_demo_profile()


async def get_user_id_or_demo(request: Request) -> str:
    """
    Returns the authenticated user's ID, or 'demo-user-001' in demo mode.
    """
    user = await get_demo_user(request)
    return user.get("user_id", "demo-user-001")


async def require_auth_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """
    STRICT auth: requires a valid Supabase JWT. Returns 401 if missing/invalid.
    Use on admin-only or strictly private endpoints.
    In demo mode (no Supabase configured), falls back to demo user with a warning.
    """
    if not settings.has_supabase:
        logger.warning("supabase_not_configured_using_demo_for_protected_route")
        return _get_demo_profile()

    auth = request.headers.get("authorization", "")
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        from app.core.security import decode_supabase_token
        token = auth.replace("Bearer ", "").strip()
        payload = decode_supabase_token(token, settings)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user ID")
        return _user_profiles.get(user_id, {"user_id": user_id, "email": payload.get("email", "")})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


def update_user_profile(user_id: str, updates: dict) -> dict:
    """Update a user's in-memory profile (used by the profile PUT endpoint)."""
    if user_id not in _user_profiles:
        _user_profiles[user_id] = _get_demo_profile()
        _user_profiles[user_id]["user_id"] = user_id
    _user_profiles[user_id].update(updates)
    return _user_profiles[user_id]
