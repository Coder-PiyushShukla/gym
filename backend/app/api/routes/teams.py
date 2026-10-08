"""
DISHA Teams & Planner API Routes.
Team matching + clash-free planner.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_demo_user
from app.schemas.common import ApiResponse
from app.schemas.team import (
    PlannerConflictRequest,
    TeamMatchRequest,
    TeamMatchResponse,
)
from app.services.team_service import compute_team_compatibility, detect_conflicts
from app.services.seed_data import SEED_OPPORTUNITIES, SEED_PLANNER_EVENTS, SEED_TEAM_CANDIDATES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.teams")

teams_router = APIRouter(prefix="/teams", tags=["Teams"])
planner_router = APIRouter(prefix="/planner", tags=["Planner"])


@teams_router.post("/match", response_model=ApiResponse)
async def find_team_matches(
    request: TeamMatchRequest,
    user: dict = Depends(get_demo_user),
):
    """
    Find complementary teammates for a specific opportunity.
    Returns candidates ranked by skill complementarity.
    """
    rid = generate_request_id()

    opp = next((o for o in SEED_OPPORTUNITIES if o.get("id") == request.opportunity_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", "Opportunity not found", rid, 404)

    candidates = []
    for candidate in SEED_TEAM_CANDIDATES:
        match = compute_team_compatibility(user, candidate, opp)
        candidates.append(match)

    # Sort by compatibility (descending)
    candidates.sort(key=lambda c: c.compatibility_score, reverse=True)

    # Compute team coverage
    required_skills = {s.lower() for s in opp.get("required_skills", [])}
    user_skills = {
        (s.get("name", s) if isinstance(s, dict) else str(s)).lower()
        for s in user.get("skills", [])
    }

    top_candidate_skills = set()
    for c in candidates[:request.target_team_size - 1]:
        top_candidate_skills |= {s.lower() for s in c.skills}

    all_team_skills = user_skills | top_candidate_skills
    coverage = {skill: skill in all_team_skills for skill in required_skills}

    response = TeamMatchResponse(
        opportunity_id=opp.get("id", ""),
        opportunity_title=opp.get("title", ""),
        user_role=_infer_user_role(user),
        candidates=[c.model_dump() for c in candidates],
        team_coverage=coverage,
    )

    return ApiResponse.ok(data=response.model_dump(), request_id=rid)


@teams_router.get("/recommendations", response_model=ApiResponse)
async def get_team_recommendations(
    user: dict = Depends(get_demo_user),
):
    """Get general team recommendations across all saved opportunities."""
    rid = generate_request_id()

    # Use the golden demo opportunity
    opp = next((o for o in SEED_OPPORTUNITIES if o.get("id") == "opp-001"), SEED_OPPORTUNITIES[0])

    candidates = []
    for candidate in SEED_TEAM_CANDIDATES:
        match = compute_team_compatibility(user, candidate, opp)
        candidates.append(match.model_dump())

    candidates.sort(key=lambda c: c["compatibility_score"], reverse=True)

    return ApiResponse.ok(data=candidates, request_id=rid)


@planner_router.post("/conflicts", response_model=ApiResponse)
async def check_planner_conflicts(
    request: PlannerConflictRequest,
    user: dict = Depends(get_demo_user),
):
    """Detect scheduling conflicts in the student's planner."""
    rid = generate_request_id()

    events = SEED_PLANNER_EVENTS
    result = detect_conflicts(events)

    return ApiResponse.ok(data=result.model_dump(), request_id=rid)


@planner_router.get("/events", response_model=ApiResponse)
async def get_planner_events(
    user: dict = Depends(get_demo_user),
):
    """Get all events in the student's planner."""
    rid = generate_request_id()
    return ApiResponse.ok(data=SEED_PLANNER_EVENTS, request_id=rid)


def _infer_user_role(profile: dict) -> str:
    """Infer the user's team role from their skills."""
    skills = {
        (s.get("name", s) if isinstance(s, dict) else str(s)).lower()
        for s in profile.get("skills", [])
    }
    career = (profile.get("career_goal") or "").lower()

    if "ml" in career or "machine learning" in career or "ai" in career:
        return "Backend/ML Developer"
    if any(s in skills for s in ["react", "vue", "angular", "figma"]):
        return "Frontend Developer"
    if any(s in skills for s in ["docker", "kubernetes", "aws"]):
        return "DevOps Engineer"
    return "Full Stack Developer"
