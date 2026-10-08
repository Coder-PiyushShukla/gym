"""
DISHA Eligibility API Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_demo_user
from app.schemas.common import ApiResponse
from app.schemas.eligibility import EligibilityCheckRequest
from app.services.eligibility_service import check_eligibility
from app.services.seed_data import SEED_OPPORTUNITIES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.eligibility")

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.post("/check", response_model=ApiResponse)
async def check_student_eligibility(
    request: EligibilityCheckRequest,
    user: dict = Depends(get_demo_user),
):
    """
    Check eligibility for a specific opportunity.
    Returns ELIGIBLE / NOT_ELIGIBLE / UNKNOWN with structured reasons.
    """
    rid = generate_request_id()

    opp = next((o for o in SEED_OPPORTUNITIES if o.get("id") == request.opportunity_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", "Opportunity not found", rid, 404)

    result = check_eligibility(user, opp)

    logger.info(
        "eligibility_checked_via_api",
        request_id=rid,
        opportunity_id=request.opportunity_id,
        status=result.status.value,
    )

    return ApiResponse.ok(data=result.model_dump(), request_id=rid)
