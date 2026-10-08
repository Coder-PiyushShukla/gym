"""
DISHA Recommendation Service.
Full recommendation pipeline: retrieve → filter → match → rank → explain.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.logging import get_logger
from app.schemas.opportunity import EligibilityStatus, OpportunityListItem
from app.schemas.recommendation import (
    MatchBreakdown,
    RecommendationItem,
    RecommendationResponse,
    SkillGap,
)
from app.services.eligibility_service import check_eligibility
from app.services.matching_service import compute_full_match
from app.services.trust_service import compute_trust_score

logger = get_logger("recommendation_service")


def generate_why_this(
    breakdown: MatchBreakdown,
    opportunity: dict,
    student_profile: dict,
    skill_gap: SkillGap,
) -> list[str]:
    """
    Generate structured "Why This?" reasons from actual matching factors.
    Each reason is derived from real data — never hallucinated.
    """
    reasons = []

    # Skill match reasons
    if breakdown.skill_match >= 70 and skill_gap.matched_skills:
        top_matches = skill_gap.matched_skills[:3]
        reasons.append(f"Matches {', '.join(top_matches)} skill{'s' if len(top_matches) > 1 else ''}")

    # Career alignment
    if breakdown.career_match >= 60:
        career = student_profile.get("career_goal", "")
        theme = opportunity.get("theme", "")
        if career and theme:
            reasons.append(f"Aligns with {career} career goal")

    # Cost
    cost = (opportunity.get("cost") or "").lower()
    if cost in ("free", "0", "$0", "₹0"):
        reasons.append("Free to participate")

    # Format
    fmt = opportunity.get("format", "")
    pref = student_profile.get("preferred_format", "")
    if pref and fmt:
        fmt_lower = fmt.lower()
        if "remote" in fmt_lower or "online" in fmt_lower:
            reasons.append("Remote participation available")
        elif "hybrid" in fmt_lower:
            reasons.append("Hybrid format — attend remotely or in person")

    # Availability
    if breakdown.availability_match >= 80:
        avail = student_profile.get("availability", "")
        if avail:
            reasons.append(f"{avail.capitalize()} schedule compatible")

    # Sustainability
    sustainability_interest = student_profile.get("sustainability_interest", False)
    sustainability_tags = opportunity.get("sustainability_tags", [])
    sdg_tags = opportunity.get("sdg_tags", [])

    if sustainability_interest and (sustainability_tags or sdg_tags):
        reasons.append("Sustainability/social impact alignment")

    # Experience level
    exp = (opportunity.get("experience_level") or "").lower()
    if "beginner" in exp or "any" in exp:
        reasons.append("Beginner-friendly opportunity")

    # High trust
    trust = opportunity.get("trust_score", 0)
    if trust >= 85:
        reasons.append(f"High trust score ({trust}/100)")

    return reasons


def generate_why_not(
    breakdown: MatchBreakdown,
    opportunity: dict,
    student_profile: dict,
    skill_gap: SkillGap,
    eligibility_status: EligibilityStatus,
    eligibility_reasons: list[str],
) -> list[str]:
    """
    Generate structured "Why Not?" limitations.
    Only includes evidence-supported concerns.
    """
    reasons = []

    # Missing skills
    if skill_gap.missing_skills:
        skills_str = ", ".join(skill_gap.missing_skills[:3])
        reasons.append(f"{skills_str} experience not in profile")

    # Eligibility uncertainty
    if eligibility_status == EligibilityStatus.UNKNOWN:
        for r in eligibility_reasons:
            if "not stated" in r.lower() or "cannot" in r.lower():
                reasons.append(r)
                break

    # Cost barrier
    if breakdown.budget_match < 40:
        cost = opportunity.get("cost", "")
        if cost:
            reasons.append(f"Registration cost: {cost}")

    # Format mismatch
    if breakdown.format_match < 40:
        fmt = opportunity.get("format", "")
        pref = student_profile.get("preferred_format", "")
        if fmt and pref:
            reasons.append(f"Format is {fmt} (preference: {pref})")

    # Team requirement
    team_min = opportunity.get("team_size_min")
    team_max = opportunity.get("team_size_max")
    if team_min and team_min > 1:
        reasons.append(f"Team of {team_min}-{team_max or team_min} required")

    # Low trust
    trust = opportunity.get("trust_score", 0)
    if trust < 60:
        reasons.append(f"Low trust score ({trust}/100) — verify before applying")

    return reasons


def build_opportunity_list_item(
    opportunity: dict,
    match_score: int = 0,
    trust_score: int = 0,
    eligibility: str = "Unknown",
    why_this: list[str] = [],
    why_not: list[str] = [],
    skill_gaps: list[str] = [],
) -> OpportunityListItem:
    """Convert opportunity dict to the format the frontend expects."""
    # Format team size for display
    team_min = opportunity.get("team_size_min")
    team_max = opportunity.get("team_size_max")
    if team_min and team_max:
        team_size = f"{team_min}-{team_max} Members"
    elif team_min:
        team_size = f"{team_min}+ Members"
    else:
        team_size = "Individual"

    # Format sustainability tags
    sdg_tags = opportunity.get("sdg_tags", [])
    sustainability_tags = opportunity.get("sustainability_tags", [])
    sustainability_display = "None"
    if sdg_tags:
        if isinstance(sdg_tags[0], dict):
            sustainability_display = sdg_tags[0].get("label", "SDG")
        else:
            sustainability_display = str(sdg_tags[0])
    elif sustainability_tags:
        sustainability_display = sustainability_tags[0] if sustainability_tags else "None"

    # Format last verified
    last_verified = opportunity.get("last_verified_at", "")
    if last_verified:
        from datetime import datetime, timezone
        try:
            dt = datetime.fromisoformat(last_verified.replace("Z", "+00:00"))
            diff = datetime.now(timezone.utc) - dt
            minutes = int(diff.total_seconds() / 60)
            if minutes < 60:
                last_verified_display = f"{minutes} mins ago"
            elif minutes < 1440:
                last_verified_display = f"{minutes // 60} hours ago"
            else:
                last_verified_display = f"{minutes // 1440} days ago"
        except Exception:
            last_verified_display = "Unknown"
    else:
        last_verified_display = "Not verified"

    return OpportunityListItem(
        id=opportunity.get("id", ""),
        title=opportunity.get("title", "Unknown"),
        organizer=opportunity.get("organizer"),
        matchScore=match_score,
        trustScore=trust_score,
        eligibility=eligibility,
        cost=opportunity.get("cost"),
        format=opportunity.get("format"),
        deadline=opportunity.get("application_deadline"),
        sustainability=sustainability_display,
        teamSize=team_size,
        lastVerified=last_verified_display,
        sources=opportunity.get("sources_count", 1),
        whyThis=why_this,
        whyNot=why_not,
        skillGaps=skill_gaps,
    )


def generate_recommendations(
    student_profile: dict,
    opportunities: list[dict],
    sources_map: dict[str, list[dict]] = {},
    evidence_map: dict[str, list[dict]] = {},
    limit: int = 10,
) -> RecommendationResponse:
    """
    Full recommendation pipeline:
    1. Compute match score for each opportunity
    2. Check eligibility
    3. Compute trust score
    4. Generate Why This / Why Not
    5. Rank by overall score
    6. Return top N
    """
    items: list[RecommendationItem] = []

    for opp in opportunities:
        opp_id = opp.get("id", "")

        # 1. Match scoring
        match_score, breakdown, skill_gap = compute_full_match(student_profile, opp)

        # 2. Eligibility check
        elig_result = check_eligibility(student_profile, opp)

        # 3. Trust score
        opp_sources = sources_map.get(opp_id, [])
        opp_evidence = evidence_map.get(opp_id, [])
        trust_result = compute_trust_score(opp, opp_sources, opp_evidence)

        # Update opportunity with computed trust score
        opp["trust_score"] = trust_result.trust_score

        # 4. Why This / Why Not
        eligibility_reason_texts = [r.reason for r in elig_result.reasons]

        why_this = generate_why_this(breakdown, opp, student_profile, skill_gap)
        why_not = generate_why_not(
            breakdown, opp, student_profile, skill_gap,
            elig_result.status, eligibility_reason_texts,
        )

        # 5. Build list item
        opp_item = build_opportunity_list_item(
            opp,
            match_score=match_score,
            trust_score=trust_result.trust_score,
            eligibility=elig_result.status.value,
            why_this=why_this,
            why_not=why_not,
            skill_gaps=skill_gap.missing_skills,
        )

        # Trust adjustment: slightly boost high-trust opportunities
        adjusted_score = match_score
        if trust_result.trust_score >= 85:
            adjusted_score = min(100, adjusted_score + 2)
        elif trust_result.trust_score < 50:
            adjusted_score = max(0, adjusted_score - 5)

        items.append(RecommendationItem(
            opportunity=opp_item,
            overall_score=adjusted_score,
            match_breakdown=breakdown,
            eligibility=elig_result.status,
            eligibility_reasons=eligibility_reason_texts,
            trust_score=trust_result.trust_score,
            why_this=why_this,
            why_not=why_not,
            skill_gap=skill_gap,
            access_score=int(breakdown.accessibility_match),
        ))

    # 6. Rank by overall score (descending)
    items.sort(key=lambda x: x.overall_score, reverse=True)

    # Limit results
    items = items[:limit]

    # Profile completeness
    profile_fields = [
        "display_name", "academic_year", "degree_type", "career_goal",
        "interests", "availability", "budget", "preferred_format",
        "skills", "experience_level",
    ]
    filled = sum(1 for f in profile_fields if student_profile.get(f))
    completeness = (filled / len(profile_fields)) * 100

    logger.info(
        "recommendations_generated",
        total_candidates=len(opportunities),
        returned=len(items),
        top_score=items[0].overall_score if items else 0,
    )

    return RecommendationResponse(
        items=items,
        total=len(items),
        profile_completeness=round(completeness, 1),
    )
