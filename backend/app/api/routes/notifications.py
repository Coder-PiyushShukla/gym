"""
DISHA Notifications API Routes.
Create, list, mark-as-read, and clear notifications.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_user_id_or_demo
from app.schemas.common import ApiResponse
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.notifications")

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory notification store: {user_id: [notif, ...]}
_notif_store: dict[str, list[dict]] = {}


def _get_user_notifs(user_id: str) -> list[dict]:
    if user_id not in _notif_store:
        # Seed with demo notifications for demo user
        _notif_store[user_id] = _seed_demo_notifications(user_id)
    return _notif_store[user_id]


def _seed_demo_notifications(user_id: str) -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "id": "notif-001",
            "profile_id": user_id,
            "type": "new_match",
            "title": "New high-match opportunity!",
            "message": "AI for Sustainable Cities Hackathon matches 94% of your profile.",
            "related_opportunity_id": "opp-001",
            "read_at": None,
            "created_at": now.isoformat(),
        },
        {
            "id": "notif-002",
            "profile_id": user_id,
            "type": "deadline_reminder",
            "title": "Deadline approaching",
            "message": "Registration deadline for Open Source Contributor Summit 2026 is in 5 days.",
            "related_opportunity_id": "opp-002",
            "read_at": None,
            "created_at": now.isoformat(),
        },
        {
            "id": "notif-003",
            "profile_id": user_id,
            "type": "team_invite",
            "title": "Team invitation",
            "message": "You've been invited to join 'ML Wizards' team for the AI Hackathon.",
            "related_opportunity_id": "opp-001",
            "read_at": None,
            "created_at": now.isoformat(),
        },
    ]


@router.get("", response_model=ApiResponse)
async def list_notifications(
    user_id: str = Depends(get_user_id_or_demo),
    unread_only: bool = Query(False),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """List notifications for the current user."""
    rid = generate_request_id()
    notifs = _get_user_notifs(user_id)

    if unread_only:
        notifs = [n for n in notifs if n.get("read_at") is None]

    total = len(notifs)
    page = notifs[offset: offset + limit]
    unread_count = sum(1 for n in _get_user_notifs(user_id) if n.get("read_at") is None)

    return ApiResponse.ok(
        data={
            "items": page,
            "total": total,
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
        },
        request_id=rid
    )


@router.patch("/{notif_id}/read", response_model=ApiResponse)
async def mark_read(
    notif_id: str,
    user_id: str = Depends(get_user_id_or_demo),
):
    """Mark a notification as read."""
    rid = generate_request_id()
    notifs = _get_user_notifs(user_id)
    for notif in notifs:
        if notif["id"] == notif_id:
            notif["read_at"] = datetime.now(timezone.utc).isoformat()
            return ApiResponse.ok(data={"updated": notif}, request_id=rid)

    from app.core.exceptions import NotFoundError
    raise NotFoundError("NOTIFICATION_NOT_FOUND", f"Notification {notif_id} not found")


@router.patch("/read-all", response_model=ApiResponse)
async def mark_all_read(user_id: str = Depends(get_user_id_or_demo)):
    """Mark all notifications as read."""
    rid = generate_request_id()
    notifs = _get_user_notifs(user_id)
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    for notif in notifs:
        if notif.get("read_at") is None:
            notif["read_at"] = now
            count += 1

    return ApiResponse.ok(data={"marked_read": count}, request_id=rid)


@router.delete("/{notif_id}", response_model=ApiResponse)
async def delete_notification(
    notif_id: str,
    user_id: str = Depends(get_user_id_or_demo),
):
    """Delete a notification."""
    rid = generate_request_id()
    notifs = _get_user_notifs(user_id)
    before = len(notifs)
    _notif_store[user_id] = [n for n in notifs if n["id"] != notif_id]

    if len(_notif_store[user_id]) == before:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("NOTIFICATION_NOT_FOUND", f"Notification {notif_id} not found")

    return ApiResponse.ok(data={"message": "Deleted"}, request_id=rid)


def create_notification(
    user_id: str,
    notif_type: str,
    title: str,
    message: str,
    opportunity_id: Optional[str] = None,
) -> dict:
    """Internal helper to create a notification (used by other services)."""
    notif = {
        "id": str(uuid.uuid4()),
        "profile_id": user_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "related_opportunity_id": opportunity_id,
        "read_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _get_user_notifs(user_id).insert(0, notif)  # newest first
    return notif
