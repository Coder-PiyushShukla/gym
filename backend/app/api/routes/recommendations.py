"""
DISHA Recommendations API Routes.
Personalized recommendations with full analysis pipeline.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_demo_user
from app.schemas.common import ApiResponse
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import generate_recommendations
from app.services.seed_data import SEED_EVIDENCE, SEED_OPPORTUNITIES, SEED_SOURCES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.recommendations")

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("", response_model=ApiResponse)
async def create_recommendations(
    request: RecommendationRequest,
    user: dict = Depends(get_demo_user),
):
    """
    Generate personalized recommendations.
    Pipeline: Profile → Candidates → Eligibility → Matching → Trust → Ranking → Explanation.
    """
    rid = generate_request_id()

    # Get opportunities (from DB or seed data)
    opps = list(SEED_OPPORTUNITIES)

    # Filter expired unless requested
    if not request.include_expired:
        opps = [o for o in opps if o.get("status") != "expired"]

    # Apply theme/format filters if provided
    if request.theme_filter:
        opps = [o for o in opps if request.theme_filter.lower() in (o.get("theme") or "").lower()]
    if request.format_filter:
        opps = [o for o in opps if request.format_filter.lower() in (o.get("format") or "").lower()]

    # Build source and evidence maps
    sources_map = {}
    for src in SEED_SOURCES:
        opp_id = src.get("opportunity_id")
        if opp_id not in sources_map:
            sources_map[opp_id] = []
        sources_map[opp_id].append(src)

    evidence_map = {}
    for ev in SEED_EVIDENCE:
        opp_id = ev.get("opportunity_id")
        if opp_id not in evidence_map:
            evidence_map[opp_id] = []
        evidence_map[opp_id].append(ev)

    # Run the full recommendation pipeline
    result = generate_recommendations(
        student_profile=user,
        opportunities=opps,
        sources_map=sources_map,
        evidence_map=evidence_map,
        limit=request.limit,
    )

    logger.info(
        "recommendations_api_response",
        request_id=rid,
        count=result.total,
    )

    return ApiResponse.ok(data=result.model_dump(), request_id=rid)


@router.get("", response_model=ApiResponse)
async def get_recommendations(
    user: dict = Depends(get_demo_user),
):
    """Get previously generated recommendations (re-generates for demo)."""
    rid = generate_request_id()

    opps = [o for o in SEED_OPPORTUNITIES if o.get("status") != "expired"]

    sources_map = {}
    for src in SEED_SOURCES:
        opp_id = src.get("opportunity_id")
        if opp_id not in sources_map:
            sources_map[opp_id] = []
        sources_map[opp_id].append(src)

    evidence_map = {}
    for ev in SEED_EVIDENCE:
        opp_id = ev.get("opportunity_id")
        if opp_id not in evidence_map:
            evidence_map[opp_id] = []
        evidence_map[opp_id].append(ev)

    result = generate_recommendations(
        student_profile=user,
        opportunities=opps,
        sources_map=sources_map,
        evidence_map=evidence_map,
        limit=10,
    )

    return ApiResponse.ok(data=result.model_dump(), request_id=rid)
