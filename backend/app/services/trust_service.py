"""
DISHA Trust Score Service.
Computes explainable trust scores from evidence, sources, and freshness.
This is REAL computation — not hardcoded values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.core.logging import get_logger
from app.schemas.opportunity import Contradiction, TrustBreakdown, TrustScoreResponse

logger = get_logger("trust_service")

# ── Weight configuration ──────────────────────────────────────
WEIGHTS = {
    "source_credibility": 0.30,
    "completeness": 0.20,
    "agreement": 0.20,
    "freshness": 0.15,
    "evidence_quality": 0.15,
}

# Known credible source domains and their credibility scores
SOURCE_CREDIBILITY_MAP = {
    "devfolio.co": 95,
    "unstop.com": 90,
    "hackerearth.com": 88,
    "kaggle.com": 92,
    "github.com": 85,
    "mlh.io": 93,
    "hackerrank.com": 88,
    "leetcode.com": 85,
    "google.com": 95,
    "microsoft.com": 95,
    "default_official": 80,
    "default_college": 70,
    "default_unknown": 50,
}

# Fields that contribute to completeness scoring
COMPLETENESS_FIELDS = [
    "title", "description", "organizer", "source_url",
    "application_deadline", "format", "cost", "eligibility_text",
    "required_skills", "start_date", "end_date",
    "team_size_min", "experience_level", "theme",
]


def compute_source_credibility(sources: list[dict]) -> float:
    """
    Score based on the credibility of data sources.
    More credible sources → higher score.
    """
    if not sources:
        return SOURCE_CREDIBILITY_MAP["default_unknown"]

    scores = []
    for source in sources:
        url = source.get("source_url", "") or ""
        name = (source.get("source_name", "") or "").lower()

        matched_score = SOURCE_CREDIBILITY_MAP["default_unknown"]
        for domain, score in SOURCE_CREDIBILITY_MAP.items():
            if domain in url.lower():
                matched_score = score
                break

        if "official" in name or "organizer" in name:
            matched_score = max(matched_score, SOURCE_CREDIBILITY_MAP["default_official"])
        elif "college" in name or "university" in name:
            matched_score = max(matched_score, SOURCE_CREDIBILITY_MAP["default_college"])

        scores.append(matched_score)

    return sum(scores) / len(scores)


def compute_field_completeness(opportunity: dict) -> float:
    """
    Score based on how many important fields are populated.
    null/empty fields reduce the score.
    """
    filled = 0
    for field in COMPLETENESS_FIELDS:
        value = opportunity.get(field)
        if value is not None and value != "" and value != []:
            filled += 1

    return (filled / len(COMPLETENESS_FIELDS)) * 100


def compute_cross_source_agreement(
    sources: list[dict],
    evidence: list[dict],
) -> tuple[float, list[Contradiction]]:
    """
    Score based on whether multiple sources agree on key fields.
    Returns (agreement_score, list of contradictions).
    """
    if len(sources) <= 1:
        # Can't compute agreement with a single source
        return 75.0, []

    contradictions: list[Contradiction] = []

    # Group evidence by field
    field_values: dict[str, list[dict[str, Any]]] = {}
    for ev in evidence:
        field = ev.get("field_name", "")
        if not field:
            continue
        if field not in field_values:
            field_values[field] = []
        field_values[field].append({
            "source": ev.get("source_name", "unknown"),
            "value": ev.get("extracted_value", ""),
            "source_url": ev.get("source_url", ""),
        })

    agreement_count = 0
    total_fields_checked = 0

    for field, values in field_values.items():
        if len(values) < 2:
            continue

        total_fields_checked += 1
        unique_values = set(v["value"].strip().lower() for v in values if v["value"])

        if len(unique_values) <= 1:
            agreement_count += 1
        else:
            contradictions.append(Contradiction(
                field_name=field,
                values=values,
                severity="high" if field in ("application_deadline", "cost", "eligibility_text") else "medium",
            ))

    if total_fields_checked == 0:
        return 75.0, contradictions

    agreement_ratio = agreement_count / total_fields_checked
    return agreement_ratio * 100, contradictions


def compute_freshness(opportunity: dict) -> float:
    """
    Score based on how recently the opportunity was verified.
    Recent verification → higher score.
    """
    last_verified = opportunity.get("last_verified_at")
    if not last_verified:
        return 40.0  # No verification = low freshness

    try:
        if isinstance(last_verified, str):
            verified_dt = datetime.fromisoformat(last_verified.replace("Z", "+00:00"))
        else:
            verified_dt = last_verified

        now = datetime.now(timezone.utc)
        hours_since = (now - verified_dt).total_seconds() / 3600

        if hours_since < 1:
            return 100.0
        elif hours_since < 6:
            return 95.0
        elif hours_since < 24:
            return 85.0
        elif hours_since < 72:
            return 70.0
        elif hours_since < 168:  # 1 week
            return 55.0
        else:
            return 40.0
    except Exception:
        return 40.0


def compute_evidence_quality(evidence: list[dict]) -> float:
    """
    Score based on the quality of extracted evidence.
    More evidence with high confidence → higher score.
    """
    if not evidence:
        return 30.0

    total_confidence = 0
    snippet_bonus = 0

    for ev in evidence:
        confidence = ev.get("confidence", 0.5)
        total_confidence += confidence

        # Bonus for having actual text snippets
        if ev.get("snippet"):
            snippet_bonus += 5

    avg_confidence = (total_confidence / len(evidence)) * 100
    snippet_score = min(snippet_bonus, 20)  # Cap snippet bonus

    return min(avg_confidence + snippet_score, 100)


def compute_trust_score(
    opportunity: dict,
    sources: list[dict],
    evidence: list[dict],
) -> TrustScoreResponse:
    """
    Compute the full explainable trust score.

    trust_score =
        0.30 * source_credibility
      + 0.20 * completeness
      + 0.20 * agreement
      + 0.15 * freshness
      + 0.15 * evidence_quality
      - contradiction_penalty
    """
    source_credibility = compute_source_credibility(sources)
    field_completeness = compute_field_completeness(opportunity)
    agreement_score, contradictions = compute_cross_source_agreement(sources, evidence)
    freshness = compute_freshness(opportunity)
    evidence_quality = compute_evidence_quality(evidence)

    # Contradiction penalty: -5 per high severity, -3 per medium
    contradiction_penalty = 0
    for c in contradictions:
        if c.severity == "high":
            contradiction_penalty += 5
        else:
            contradiction_penalty += 3

    raw_score = (
        WEIGHTS["source_credibility"] * source_credibility
        + WEIGHTS["completeness"] * field_completeness
        + WEIGHTS["agreement"] * agreement_score
        + WEIGHTS["freshness"] * freshness
        + WEIGHTS["evidence_quality"] * evidence_quality
        - contradiction_penalty
    )

    trust_score = max(0, min(100, int(round(raw_score))))

    breakdown = TrustBreakdown(
        source_credibility=round(source_credibility, 1),
        field_completeness=round(field_completeness, 1),
        cross_source_agreement=round(agreement_score, 1),
        freshness=round(freshness, 1),
        evidence_quality=round(evidence_quality, 1),
        contradiction_penalty=round(contradiction_penalty, 1),
    )

    logger.info(
        "trust_score_calculated",
        trust_score=trust_score,
        contradictions=len(contradictions),
        sources=len(sources),
    )

    return TrustScoreResponse(
        trust_score=trust_score,
        breakdown=breakdown,
        sources_count=len(sources),
        last_verified_at=opportunity.get("last_verified_at"),
        contradictions=contradictions,
    )
