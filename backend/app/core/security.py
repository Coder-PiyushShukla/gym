"""
DISHA Security Utilities.
JWT verification via Supabase Auth, request helpers.
"""

from __future__ import annotations

from typing import Any, Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("security")

# Supabase JWTs are signed with the JWT secret derived from the project.
# For verification we use the anon key as the HMAC secret (HS256).
ALGORITHM = "HS256"


def decode_supabase_token(
    token: str,
    settings: Settings,
) -> dict[str, Any]:
    """
    Decode and verify a Supabase-issued JWT.
    Returns the payload dict with 'sub' (user id), 'email', 'role', etc.
    """
    try:
        payload = jwt.decode(
            token,
            settings.supabase_anon_key,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """
    FastAPI dependency: extract and verify the Bearer token.
    Returns the decoded JWT payload.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    payload = decode_supabase_token(token, settings)
    return payload


async def get_current_user_id(
    user: dict[str, Any] = Depends(get_current_user),
) -> str:
    """FastAPI dependency: return just the user id (sub claim)."""
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user id")
    return user_id


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings),
) -> Optional[dict[str, Any]]:
    """
    FastAPI dependency: optionally extract user.
    Returns None if no token is provided (public endpoints).
    """
    if not authorization:
        return None
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        return decode_supabase_token(token, settings)
    except Exception:
        return None
