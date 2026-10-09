"""
DISHA User Profile API Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_demo_user, get_user_id_or_demo, update_user_profile
from app.schemas.common import ApiResponse
from app.schemas.user import ProfileResponse, StudentProfileUpdate
from app.services.seed_data import DEMO_STUDENT_PROFILE
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.users")

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ApiResponse)
async def get_profile(user: dict = Depends(get_demo_user)):
    """Get the current user's profile."""
    rid = generate_request_id()

    profile = ProfileResponse(
        user_id=user.get("user_id", ""),
        display_name=user.get("display_name"),
        academic_year=user.get("academic_year"),
        degree_type=user.get("degree_type"),
        institution=user.get("institution"),
        career_goal=user.get("career_goal"),
        interests=user.get("interests", []),
        availability=user.get("availability"),
        budget=user.get("budget"),
        preferred_format=user.get("preferred_format"),
        location=user.get("location"),
        experience_level=user.get("experience_level"),
        sustainability_interest=user.get("sustainability_interest", False),
        skills=user.get("skills", []),
        allow_eligibility_check=user.get("allow_eligibility_check", True),
        allow_team_visibility=user.get("allow_team_visibility", True),
        allow_external_scraping=user.get("allow_external_scraping", False),
    )

    return ApiResponse.ok(data=profile.model_dump(), request_id=rid)


@router.put("", response_model=ApiResponse)
async def update_profile(
    update: StudentProfileUpdate,
    request: Request,
    user: dict = Depends(get_demo_user),
):
    """Update the current user's profile. Changes persist for the session."""
    rid = generate_request_id()

    update_data = update.model_dump(exclude_none=True)
    user_id = user.get("user_id", "demo-user-001")

    # Persist update in the in-memory store (keyed by user_id)
    update_user_profile(user_id, update_data)

    logger.info("profile_updated", request_id=rid, user_id=user_id, fields=list(update_data.keys()))

    return ApiResponse.ok(data={"updated_fields": list(update_data.keys())}, request_id=rid)
