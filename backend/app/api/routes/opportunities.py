"""
DISHA Opportunities API Routes.
CRUD + search + evidence + trust endpoints for opportunities.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_demo_user, get_user_id_or_demo
from app.schemas.common import ApiResponse
from app.schemas.opportunity import (
    OpportunityListItem,
    OpportunityResponse,
    OpportunitySearchRequest,
    OpportunitySearchResponse,
    EvidenceResponse,
    TrustScoreResponse,
)
from app.services.seed_data import SEED_EVIDENCE, SEED_OPPORTUNITIES, SEED_SOURCES
from app.services.trust_service import compute_trust_score
from app.services.recommendation_service import build_opportunity_list_item
from app.services.matching_service import compute_full_match
from app.services.scraping_service import fetch_all_live_opportunities
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.opportunities")

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

# ── In-memory store (falls back to seed data when Supabase unavailable) ──
_opportunities_store: list[dict] = []
_evidence_store: list[dict] = []
_sources_store: list[dict] = []


def _get_opps() -> list[dict]:
    return _opportunities_store if _opportunities_store else SEED_OPPORTUNITIES


def _get_evidence(opp_id: str) -> list[dict]:
    store = _evidence_store if _evidence_store else SEED_EVIDENCE
    return [e for e in store if e.get("opportunity_id") == opp_id]


def _get_sources(opp_id: str) -> list[dict]:
    store = _sources_store if _sources_store else SEED_SOURCES
    return [s for s in store if s.get("opportunity_id") == opp_id]

@router.post("/sync", response_model=ApiResponse)
async def sync_live_opportunities():
    """Fetch live data from Devfolio and Unstop via scraping service."""
    rid = generate_request_id()
    global _opportunities_store
    live_data = await fetch_all_live_opportunities()
    
    # We keep the SEED_OPPORTUNITIES (golden demo data) and append live data
    _opportunities_store = SEED_OPPORTUNITIES + live_data
    
    return ApiResponse.ok(
        data={"message": f"Successfully synced {len(live_data)} live opportunities. Total now {len(_opportunities_store)}."},
        request_id=rid
    )


@router.get("", response_model=ApiResponse)
async def list_opportunities(
    theme: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    is_free: Optional[bool] = Query(None),
    experience_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="active, expired, unverified"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """List opportunities with optional filters."""
    rid = generate_request_id()
    opps = _get_opps()

    # Apply filters
    filtered = []
    for opp in opps:
        if status and opp.get("status") != status:
            continue
        if status is None and opp.get("status") == "expired":
            continue  # Default: exclude expired
        if theme and theme.lower() not in (opp.get("theme") or "").lower():
            continue
        if format and format.lower() not in (opp.get("format") or "").lower():
            continue
        if is_remote is not None and opp.get("is_remote") != is_remote:
            continue
        if is_free and (opp.get("cost") or "").lower() not in ("free", "0", "$0", "₹0"):
            continue
        if experience_level and opp.get("experience_level") != experience_level:
            continue
        filtered.append(opp)

    total = len(filtered)
    page = filtered[offset : offset + limit]

    items = []
    for opp in page:
        items.append(build_opportunity_list_item(
            opp,
            trust_score=opp.get("trust_score", 0),
        ))

    return ApiResponse.ok(
        data={
            "items": [item.model_dump() for item in items],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        },
        request_id=rid,
    )


@router.get("/{opp_id}", response_model=ApiResponse)
async def get_opportunity(opp_id: str):
    """Get a single opportunity by ID with full details."""
    rid = generate_request_id()
    opps = _get_opps()

    opp = next((o for o in opps if o.get("id") == opp_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", f"Opportunity '{opp_id}' not found", rid, 404)

    return ApiResponse.ok(data=opp, request_id=rid)


@router.post("/search", response_model=ApiResponse)
async def search_opportunities(
    request: OpportunitySearchRequest,
    user: dict = Depends(get_demo_user),
):
    """
    Search opportunities with natural language + structured filters.
    Pipeline: NL → intent extraction → structured filters → semantic search → ranking.
    """
    rid = generate_request_id()
    opps = _get_opps()

    # Parse natural language query into filters
    parsed_filters = {}
    if request.query:
        parsed_filters = _parse_nl_query(request.query)

    # Merge explicit filters with parsed ones (explicit takes priority)
    effective_filters = {**parsed_filters}
    if request.theme:
        effective_filters["theme"] = request.theme
    if request.format:
        effective_filters["format"] = request.format
    if request.is_remote is not None:
        effective_filters["is_remote"] = request.is_remote
    if request.is_free is not None:
        effective_filters["is_free"] = request.is_free
    if request.experience_level:
        effective_filters["experience_level"] = request.experience_level

    # Apply filters
    filtered = []
    for opp in opps:
        if opp.get("status") == "expired":
            continue

        theme_filter = effective_filters.get("theme")
        if theme_filter and theme_filter.lower() not in (opp.get("theme") or "").lower():
            # Also check tags and description
            tags = " ".join(opp.get("sustainability_tags", []) + [t.get("label", "") for t in opp.get("sdg_tags", []) if isinstance(t, dict)])
            desc = (opp.get("description") or "").lower()
            if theme_filter.lower() not in tags.lower() and theme_filter.lower() not in desc:
                continue

        fmt_filter = effective_filters.get("format")
        if fmt_filter and fmt_filter.lower() not in (opp.get("format") or "").lower():
            continue

        if effective_filters.get("is_remote") and not opp.get("is_remote"):
            continue

        if effective_filters.get("is_free"):
            cost = (opp.get("cost") or "").lower()
            if cost not in ("free", "0", "$0", "₹0", ""):
                continue

        exp = effective_filters.get("experience_level")
        if exp and opp.get("experience_level") and exp not in opp.get("experience_level", ""):
            continue

        filtered.append(opp)

    # Score and rank with matching
    scored_items = []
    for opp in filtered:
        match_score, breakdown, skill_gap = compute_full_match(user, opp)
        item = build_opportunity_list_item(
            opp,
            match_score=match_score,
            trust_score=opp.get("trust_score", 0),
            skill_gaps=skill_gap.missing_skills,
        )
        scored_items.append((match_score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)
    page = scored_items[request.offset : request.offset + request.limit]

    return ApiResponse.ok(
        data=OpportunitySearchResponse(
            items=[item for _, item in page],
            total=len(scored_items),
            parsed_filters=parsed_filters if parsed_filters else None,
            has_more=(request.offset + request.limit) < len(scored_items),
        ).model_dump(),
        request_id=rid,
    )


@router.get("/{opp_id}/evidence", response_model=ApiResponse)
async def get_opportunity_evidence(opp_id: str):
    """Get evidence cards for an opportunity."""
    rid = generate_request_id()
    evidence = _get_evidence(opp_id)

    cards = []
    for ev in evidence:
        value = ev.get("extracted_value")
        source = ev.get("source_name")

        if value is None or value == "":
            status = "Not Stated"
        else:
            status = "Verified"

        cards.append(EvidenceResponse(
            field=ev.get("field_name", "Unknown"),
            value=value,
            source=source,
            status=status,
        ).model_dump())

    return ApiResponse.ok(data=cards, request_id=rid)


@router.get("/{opp_id}/trust", response_model=ApiResponse)
async def get_opportunity_trust(opp_id: str):
    """Get the full trust score breakdown for an opportunity."""
    rid = generate_request_id()

    opps = _get_opps()
    opp = next((o for o in opps if o.get("id") == opp_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", "Opportunity not found", rid, 404)

    sources = _get_sources(opp_id)
    evidence = _get_evidence(opp_id)

    trust_result = compute_trust_score(opp, sources, evidence)
    return ApiResponse.ok(data=trust_result.model_dump(), request_id=rid)


def _parse_nl_query(query: str) -> dict:
    """
    Simple NL intent extraction.
    In production this would use Gemini; for demo we use keyword matching.
    """
    query_lower = query.lower()
    filters = {}

    # Theme detection
    theme_keywords = {
        "ai": "AI/ML", "ml": "AI/ML", "machine learning": "AI/ML",
        "web": "Web Development", "frontend": "Web Development",
        "cyber": "Cybersecurity", "security": "Cybersecurity",
        "data": "Data Science", "data science": "Data Science",
        "blockchain": "Web3/Blockchain", "web3": "Web3/Blockchain",
        "sustainability": "Sustainability", "climate": "Sustainability",
        "open source": "Open Source",
        "robotics": "Robotics/AI",
        "social": "Social Impact",
    }
    for keyword, theme in theme_keywords.items():
        if keyword in query_lower:
            filters["theme"] = theme
            break

    # Format detection
    if "remote" in query_lower or "online" in query_lower:
        filters["is_remote"] = True
    if "in-person" in query_lower or "offline" in query_lower:
        filters["format"] = "In-Person"

    # Cost detection
    if "free" in query_lower or "no cost" in query_lower:
        filters["is_free"] = True

    # Level detection
    if "beginner" in query_lower:
        filters["experience_level"] = "beginner"
    elif "advanced" in query_lower:
        filters["experience_level"] = "advanced"

    return filters
