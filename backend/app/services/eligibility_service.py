"""
DISHA Eligibility Service.
Evaluates student eligibility against opportunity requirements.
SEPARATE from relevance/matching — this checks if the student CAN participate.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.logging import get_logger
from app.schemas.opportunity import EligibilityStatus, EligibilityStructured
from app.schemas.eligibility import EligibilityCheckResponse, EligibilityReason

logger = get_logger("eligibility_service")


def check_eligibility(
    student_profile: dict,
    opportunity: dict,
) -> EligibilityCheckResponse:
    """
    Evaluate whether a student is eligible for an opportunity.

    Rules:
    - If the opportunity doesn't state a requirement → UNKNOWN (never assume)
    - If the student matches a stated requirement → ELIGIBLE for that criterion
    - If the student doesn't match a stated requirement → NOT_ELIGIBLE

    The overall status is the WORST of all individual checks:
    NOT_ELIGIBLE > UNKNOWN > ELIGIBLE
    """
    reasons: list[EligibilityReason] = []

    # Parse structured eligibility from opportunity
    elig_data = opportunity.get("eligibility_structured")
    elig_text = opportunity.get("eligibility_text", "")

    if isinstance(elig_data, dict):
        structured = EligibilityStructured(**elig_data)
    elif isinstance(elig_data, EligibilityStructured):
        structured = elig_data
    else:
        structured = EligibilityStructured()

    # ── Academic Year Check ────────────────────────────────────
    student_year = student_profile.get("academic_year")
    required_years = structured.academic_year

    if required_years:
        if student_year is not None:
            year_str = str(student_year)
            year_labels = [str(y) for y in required_years]
            # Check various formats: "2", "2nd year", "undergraduate"
            is_match = (
                year_str in year_labels
                or any("undergraduate" in y.lower() for y in year_labels)
                or any(f"year {year_str}" in y.lower() for y in year_labels)
            )
            if is_match:
                reasons.append(EligibilityReason(
                    field="academic_year",
                    status=EligibilityStatus.ELIGIBLE,
                    reason=f"Year {student_year} matches requirement: {', '.join(required_years)}",
                ))
            else:
                reasons.append(EligibilityReason(
                    field="academic_year",
                    status=EligibilityStatus.NOT_ELIGIBLE,
                    reason=f"Year {student_year} does not match: {', '.join(required_years)}",
                ))
        else:
            reasons.append(EligibilityReason(
                field="academic_year",
                status=EligibilityStatus.UNKNOWN,
                reason="Student has not specified academic year",
            ))
    else:
        reasons.append(EligibilityReason(
            field="academic_year",
            status=EligibilityStatus.UNKNOWN,
            reason="Academic year requirement not stated by organizer",
        ))

    # ── Degree Type Check ──────────────────────────────────────
    student_degree = student_profile.get("degree_type", "")
    required_degrees = structured.degree_type

    if required_degrees:
        if student_degree:
            is_match = any(
                d.lower() in student_degree.lower()
                or student_degree.lower() in d.lower()
                or "undergraduate" in d.lower()
                for d in required_degrees
            )
            if is_match:
                reasons.append(EligibilityReason(
                    field="degree_type",
                    status=EligibilityStatus.ELIGIBLE,
                    reason=f"Degree '{student_degree}' matches: {', '.join(required_degrees)}",
                ))
            else:
                reasons.append(EligibilityReason(
                    field="degree_type",
                    status=EligibilityStatus.NOT_ELIGIBLE,
                    reason=f"Degree '{student_degree}' does not match: {', '.join(required_degrees)}",
                ))
        else:
            reasons.append(EligibilityReason(
                field="degree_type",
                status=EligibilityStatus.UNKNOWN,
                reason="Student has not specified degree type",
            ))
    # If opportunity doesn't specify → no constraint, don't add UNKNOWN

    # ── Age Check ──────────────────────────────────────────────
    age_range = structured.age_range
    # We don't store student age, so always UNKNOWN if there's a constraint
    if age_range:
        reasons.append(EligibilityReason(
            field="age",
            status=EligibilityStatus.UNKNOWN,
            reason=f"Age requirement ({age_range}) cannot be verified — age not in profile",
        ))

    # ── Nationality Check ──────────────────────────────────────
    required_nationalities = structured.nationality
    student_location = student_profile.get("location", "")

    if required_nationalities:
        if student_location:
            is_match = any(
                n.lower() in student_location.lower()
                or student_location.lower() in n.lower()
                or n.lower() == "international"
                or n.lower() == "any"
                for n in required_nationalities
            )
            if is_match:
                reasons.append(EligibilityReason(
                    field="nationality",
                    status=EligibilityStatus.ELIGIBLE,
                    reason=f"Location '{student_location}' matches: {', '.join(required_nationalities)}",
                ))
            else:
                reasons.append(EligibilityReason(
                    field="nationality",
                    status=EligibilityStatus.UNKNOWN,
                    reason=f"Cannot determine if '{student_location}' satisfies: {', '.join(required_nationalities)}",
                ))
        else:
            reasons.append(EligibilityReason(
                field="nationality",
                status=EligibilityStatus.UNKNOWN,
                reason="Student location not specified; cannot check nationality requirement",
            ))

    # ── Custom Requirements ────────────────────────────────────
    for req in structured.custom_requirements:
        reasons.append(EligibilityReason(
            field="custom",
            status=EligibilityStatus.UNKNOWN,
            reason=f"Custom requirement cannot be automatically verified: '{req}'",
        ))

    # ── Fallback: if only eligibility_text and no structured ───
    if not reasons and elig_text:
        text_lower = elig_text.lower()
        # Heuristic checks on free text
        if "open to all" in text_lower or "anyone" in text_lower:
            reasons.append(EligibilityReason(
                field="general",
                status=EligibilityStatus.ELIGIBLE,
                reason=f"Eligibility text states: '{elig_text}'",
            ))
        elif "undergraduate" in text_lower or "college student" in text_lower:
            if student_year and 1 <= student_year <= 4:
                reasons.append(EligibilityReason(
                    field="general",
                    status=EligibilityStatus.ELIGIBLE,
                    reason=f"Student is an undergraduate (year {student_year}), matches: '{elig_text}'",
                ))
            else:
                reasons.append(EligibilityReason(
                    field="general",
                    status=EligibilityStatus.UNKNOWN,
                    reason=f"Cannot verify against: '{elig_text}'",
                ))
        else:
            reasons.append(EligibilityReason(
                field="general",
                status=EligibilityStatus.UNKNOWN,
                reason=f"Cannot automatically verify eligibility: '{elig_text}'",
            ))

    if not reasons:
        reasons.append(EligibilityReason(
            field="general",
            status=EligibilityStatus.UNKNOWN,
            reason="No eligibility requirements stated by organizer",
        ))

    # ── Determine overall status ───────────────────────────────
    statuses = [r.status for r in reasons]

    if EligibilityStatus.NOT_ELIGIBLE in statuses:
        overall = EligibilityStatus.NOT_ELIGIBLE
    elif all(s == EligibilityStatus.ELIGIBLE for s in statuses):
        overall = EligibilityStatus.ELIGIBLE
    elif EligibilityStatus.ELIGIBLE in statuses and EligibilityStatus.UNKNOWN in statuses:
        # Some criteria met, some unknown — lean toward eligible but flag uncertainty
        overall = EligibilityStatus.ELIGIBLE
    else:
        overall = EligibilityStatus.UNKNOWN

    logger.info(
        "eligibility_checked",
        overall=overall.value,
        criteria_count=len(reasons),
    )

    return EligibilityCheckResponse(status=overall, reasons=reasons)
