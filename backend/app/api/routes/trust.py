"""
DISHA Trust API Routes.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services.trust_service import compute_trust_score
from app.services.seed_data import SEED_EVIDENCE, SEED_OPPORTUNITIES, SEED_SOURCES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.trust")

router = APIRouter(prefix="/trust", tags=["Trust & Evidence"])


@router.get("/{opp_id}", response_model=ApiResponse)
async def get_trust_score(opp_id: str):
    """Get explainable trust score for an opportunity."""
    rid = generate_request_id()

    opp = next((o for o in SEED_OPPORTUNITIES if o.get("id") == opp_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", "Opportunity not found", rid, 404)

    sources = [s for s in SEED_SOURCES if s.get("opportunity_id") == opp_id]
    evidence = [e for e in SEED_EVIDENCE if e.get("opportunity_id") == opp_id]

    result = compute_trust_score(opp, sources, evidence)

    return ApiResponse.ok(data=result.model_dump(), request_id=rid)
