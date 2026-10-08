"""
DISHA Verification Service.
Deduplication engine and verification run tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Optional
from urllib.parse import urlparse

from app.core.logging import get_logger

logger = get_logger("verification_service")

# Thresholds
TITLE_SIMILARITY_THRESHOLD = 0.80
ORGANIZER_SIMILARITY_THRESHOLD = 0.75
COMBINED_DEDUP_THRESHOLD = 0.85


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_url(url: str) -> str:
    """Canonicalize a URL for dedup comparison."""
    try:
        parsed = urlparse(url.lower().strip())
        # Remove www, trailing slashes, query params for comparison
        host = parsed.netloc.replace("www.", "")
        path = parsed.path.rstrip("/")
        return f"{host}{path}"
    except Exception:
        return url.lower().strip()


def text_similarity(a: str, b: str) -> float:
    """Compute text similarity ratio using SequenceMatcher."""
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def check_duplicate(
    new_opp: dict,
    existing_opps: list[dict],
) -> Optional[dict]:
    """
    Multi-stage deduplication check.

    Stage 1: Normalized title similarity
    Stage 2: Organizer similarity
    Stage 3: Date similarity
    Stage 4: URL canonicalization
    Stage 5: Combined score threshold

    Returns the matched existing opportunity if duplicate found, else None.
    """
    new_title = new_opp.get("title", "")
    new_org = new_opp.get("organizer", "")
    new_url = new_opp.get("source_url", "")
    new_deadline = new_opp.get("application_deadline", "")

    for existing in existing_opps:
        score = 0
        checks = 0

        # Stage 1: Title
        ex_title = existing.get("title", "")
        if new_title and ex_title:
            title_sim = text_similarity(new_title, ex_title)
            if title_sim >= TITLE_SIMILARITY_THRESHOLD:
                score += title_sim * 0.4
            checks += 0.4

        # Stage 2: Organizer
        ex_org = existing.get("organizer", "")
        if new_org and ex_org:
            org_sim = text_similarity(new_org, ex_org)
            if org_sim >= ORGANIZER_SIMILARITY_THRESHOLD:
                score += org_sim * 0.2
            checks += 0.2

        # Stage 3: Deadline similarity
        ex_deadline = existing.get("application_deadline", "")
        if new_deadline and ex_deadline:
            if normalize_text(new_deadline) == normalize_text(ex_deadline):
                score += 0.2
            checks += 0.2

        # Stage 4: URL canonicalization
        ex_url = existing.get("source_url", "")
        if new_url and ex_url:
            if normalize_url(new_url) == normalize_url(ex_url):
                score += 0.2  # Same URL = strong dedup signal
            checks += 0.2

        # Stage 5: Combined threshold
        if checks > 0 and (score / checks) >= COMBINED_DEDUP_THRESHOLD:
            logger.info(
                "duplicate_detected",
                new_title=new_title,
                existing_title=ex_title,
                similarity=round(score / checks, 3),
            )
            return existing

    return None


def merge_duplicate_evidence(
    canonical: dict,
    duplicate: dict,
) -> dict:
    """
    Merge evidence from a duplicate into the canonical opportunity.
    Don't delete information — add source provenance.
    """
    # Merge sources
    existing_sources = canonical.get("_sources", [])
    dup_source = {
        "source_url": duplicate.get("source_url"),
        "source_name": duplicate.get("source_name"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    existing_sources.append(dup_source)
    canonical["_sources"] = existing_sources

    # Increment sources count
    canonical["sources_count"] = canonical.get("sources_count", 1) + 1

    # Fill in missing fields from duplicate (don't overwrite existing)
    for field in ["description", "theme", "eligibility_text", "start_date",
                  "end_date", "cost", "format", "location", "experience_level"]:
        if not canonical.get(field) and duplicate.get(field):
            canonical[field] = duplicate[field]

    return canonical
