"""
DISHA Admin API Routes.
Protected endpoints for seeding, ingestion, and system management.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services.seed_data import SEED_EVIDENCE, SEED_OPPORTUNITIES, SEED_SOURCES
from app.services.verification_service import check_duplicate
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/seed", response_model=ApiResponse)
async def seed_database():
    """Seed the database with demo data."""
    rid = generate_request_id()

    # In demo mode, data is already in memory via seed_data.py
    # In production, this would insert into Supabase

    # Run deduplication check on seed data
    dedup_count = 0
    canonical_opps = []
    for opp in SEED_OPPORTUNITIES:
        dup = check_duplicate(opp, canonical_opps)
        if dup:
            dedup_count += 1
            logger.info(
                "seed_duplicate_found",
                new=opp.get("title"),
                existing=dup.get("title"),
            )
        else:
            canonical_opps.append(opp)

    result = {
        "seeded_at": datetime.now(timezone.utc).isoformat(),
        "opportunities": len(SEED_OPPORTUNITIES),
        "canonical_opportunities": len(canonical_opps),
        "duplicates_found": dedup_count,
        "evidence_records": len(SEED_EVIDENCE),
        "source_records": len(SEED_SOURCES),
    }

    logger.info("database_seeded", **result)

    return ApiResponse.ok(data=result, request_id=rid)


@router.post("/ingestion/run", response_model=ApiResponse)
async def trigger_ingestion():
    """Trigger a manual ingestion run."""
    rid = generate_request_id()

    # For demo: simulate an ingestion run
    result = {
        "run_id": f"run-{rid}",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "sources_processed": 3,
        "records_processed": len(SEED_OPPORTUNITIES),
        "records_created": 0,
        "records_updated": len(SEED_OPPORTUNITIES),
        "duplicates_found": 1,
        "contradictions_found": 1,
        "errors": 0,
    }

    logger.info("ingestion_run_completed", **result)

    return ApiResponse.ok(data=result, request_id=rid)


@router.get("/ingestion/status", response_model=ApiResponse)
async def get_ingestion_status():
    """Get the status of the last ingestion run."""
    rid = generate_request_id()

    return ApiResponse.ok(
        data={
            "last_run": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "total_opportunities": len(SEED_OPPORTUNITIES),
            "active_sources": 3,
            "next_scheduled_run": None,
        },
        request_id=rid,
    )


@router.post("/recalculate-trust", response_model=ApiResponse)
async def recalculate_trust():
    """Recalculate trust scores for all opportunities."""
    rid = generate_request_id()
    from app.services.trust_service import compute_trust_score

    results = []
    for opp in SEED_OPPORTUNITIES:
        opp_id = opp.get("id", "")
        sources = [s for s in SEED_SOURCES if s.get("opportunity_id") == opp_id]
        evidence = [e for e in SEED_EVIDENCE if e.get("opportunity_id") == opp_id]

        trust = compute_trust_score(opp, sources, evidence)
        results.append({
            "opportunity_id": opp_id,
            "title": opp.get("title", ""),
            "old_trust_score": opp.get("trust_score", 0),
            "new_trust_score": trust.trust_score,
            "contradictions": len(trust.contradictions),
        })

    return ApiResponse.ok(data=results, request_id=rid)
