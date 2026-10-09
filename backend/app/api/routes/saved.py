"""
DISHA Saved Opportunities API Routes.
Save, unsave, list, and update application status for saved opportunities.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_demo_user, get_user_id_or_demo
from app.schemas.common import ApiResponse
from app.services.seed_data import SEED_OPPORTUNITIES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.saved")

router = APIRouter(prefix="/saved", tags=["Saved Opportunities"])

# In-memory saved store: {user_id: [saved_record, ...]}
_saved_store: dict[str, list[dict]] = {}


def _get_user_saved(user_id: str) -> list[dict]:
    return _saved_store.setdefault(user_id, [])


def _find_opp(opp_id: str) -> Optional[dict]:
    for opp in SEED_OPPORTUNITIES:
        if opp.get("id") == opp_id:
            return opp
    return None


@router.get("", response_model=ApiResponse)
async def list_saved(
    user_id: str = Depends(get_user_id_or_demo),
    application_status: Optional[str] = Query(None),
):
    """List all saved opportunities for the current user."""
    rid = generate_request_id()
    saved = _get_user_saved(user_id)

    if application_status:
        saved = [s for s in saved if s.get("application_status") == application_status]

    # Enrich with opportunity data
    result = []
    for s in saved:
        opp = _find_opp(s["opportunity_id"])
        if opp:
            result.append({**s, "opportunity": opp})

    return ApiResponse.ok(
        data={"items": result, "total": len(result)},
        request_id=rid
    )


@router.post("/{opp_id}", response_model=ApiResponse)
async def save_opportunity(
    opp_id: str,
    user_id: str = Depends(get_user_id_or_demo),
):
    """Save an opportunity for the current user."""
    rid = generate_request_id()
    saved = _get_user_saved(user_id)

    # Check for duplicate
    for s in saved:
        if s["opportunity_id"] == opp_id:
            return ApiResponse.ok(
                data={"message": "Already saved", "saved": s},
                request_id=rid
            )

    opp = _find_opp(opp_id)
    if not opp:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("OPPORTUNITY_NOT_FOUND", f"Opportunity {opp_id} not found")

    record = {
        "id": str(uuid.uuid4()),
        "profile_id": user_id,
        "opportunity_id": opp_id,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "personal_notes": None,
        "application_status": "considering",
    }
    saved.append(record)

    logger.info("opportunity_saved", user_id=user_id, opp_id=opp_id)
    return ApiResponse.ok(data={"message": "Saved", "saved": record}, request_id=rid)


@router.delete("/{opp_id}", response_model=ApiResponse)
async def unsave_opportunity(
    opp_id: str,
    user_id: str = Depends(get_user_id_or_demo),
):
    """Unsave/remove an opportunity from the user's saved list."""
    rid = generate_request_id()
    saved = _get_user_saved(user_id)
    before = len(saved)
    _saved_store[user_id] = [s for s in saved if s["opportunity_id"] != opp_id]

    if len(_saved_store[user_id]) == before:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("NOT_SAVED", f"Opportunity {opp_id} is not in your saved list")

    logger.info("opportunity_unsaved", user_id=user_id, opp_id=opp_id)
    return ApiResponse.ok(data={"message": "Removed from saved"}, request_id=rid)


@router.patch("/{opp_id}/status", response_model=ApiResponse)
async def update_application_status(
    opp_id: str,
    status: str,
    notes: Optional[str] = None,
    user_id: str = Depends(get_user_id_or_demo),
):
    """Update application status for a saved opportunity."""
    rid = generate_request_id()
    VALID_STATUSES = ("considering", "applied", "accepted", "rejected", "withdrawn")
    if status not in VALID_STATUSES:
        from app.core.exceptions import ValidationError as DishaValidationError
        raise DishaValidationError("INVALID_STATUS", f"Status must be one of: {', '.join(VALID_STATUSES)}")

    saved = _get_user_saved(user_id)
    for s in saved:
        if s["opportunity_id"] == opp_id:
            s["application_status"] = status
            if notes is not None:
                s["personal_notes"] = notes
            return ApiResponse.ok(data={"updated": s}, request_id=rid)

    from app.core.exceptions import NotFoundError
    raise NotFoundError("NOT_SAVED", f"Opportunity {opp_id} is not in your saved list")
