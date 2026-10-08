"""
DISHA Team Service.
Complementary skill matching for team formation.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.logging import get_logger
from app.schemas.team import (
    PlannerConflict,
    PlannerConflictResponse,
    PlannerEvent,
    TeamMatchCandidate,
    TeamMatchResponse,
)

logger = get_logger("team_service")


def _get_skill_names(profile: dict) -> set[str]:
    """Extract normalized skill names from a profile."""
    skills = profile.get("skills", [])
    return {
        (s.get("name", s) if isinstance(s, dict) else str(s)).lower().strip()
        for s in skills
    }


def compute_team_compatibility(
    student_profile: dict,
    candidate_profile: dict,
    opportunity: dict,
) -> TeamMatchCandidate:
    """
    Compute complementary compatibility between two students.
    High score = they bring DIFFERENT skills that the team needs.
    """
    student_skills = _get_skill_names(student_profile)
    candidate_skills = _get_skill_names(candidate_profile)

    required_skills = {s.lower().strip() for s in opportunity.get("required_skills", [])}

    # Complementary = skills they have that the student doesn't
    complementary = candidate_skills - student_skills
    shared = student_skills & candidate_skills

    # Team coverage: what required skills are covered by both together
    combined_skills = student_skills | candidate_skills
    covered_required = required_skills & combined_skills
    missing_required = required_skills - combined_skills

    # Complementarity score: more unique skills → higher score
    if candidate_skills:
        complementary_ratio = len(complementary) / len(candidate_skills)
    else:
        complementary_ratio = 0

    # Skill coverage bonus
    if required_skills:
        coverage_ratio = len(covered_required) / len(required_skills)
    else:
        coverage_ratio = 0.5

    # Interest overlap
    student_interests = set(i.lower() for i in student_profile.get("interests", []))
    candidate_interests = set(i.lower() for i in candidate_profile.get("interests", []))
    shared_interests = student_interests & candidate_interests

    # Availability overlap
    student_avail = (student_profile.get("availability") or "").lower()
    candidate_avail = (candidate_profile.get("availability") or "").lower()
    avail_overlap = None
    if student_avail and candidate_avail:
        if student_avail == candidate_avail:
            avail_overlap = student_avail.capitalize()
        elif "flexible" in student_avail or "flexible" in candidate_avail:
            avail_overlap = "Flexible"

    # Score: weight complementarity heavily (we want DIFFERENT skills)
    score = int(round(
        complementary_ratio * 50     # 50% weight on bringing different skills
        + coverage_ratio * 30        # 30% weight on covering required skills together
        + (len(shared_interests) / max(len(student_interests), 1)) * 10  # 10% shared interests
        + (10 if avail_overlap else 0)  # 10% availability match
    ))

    score = max(0, min(100, score))

    # AI reasoning
    reasoning_parts = []
    if complementary:
        reasoning_parts.append(
            f"Brings {', '.join(list(complementary)[:3]).title()} skills you don't have"
        )
    if shared:
        reasoning_parts.append(
            f"Shares knowledge in {', '.join(list(shared)[:2]).title()}"
        )
    if missing_required:
        reasoning_parts.append(
            f"Team still needs: {', '.join(list(missing_required)[:2]).title()}"
        )
    if not reasoning_parts:
        reasoning_parts.append("General compatibility based on profile analysis")

    reasoning = ". ".join(reasoning_parts) + "."

    # Determine role
    role = _infer_role(candidate_skills)

    return TeamMatchCandidate(
        user_id=candidate_profile.get("user_id", ""),
        display_name=candidate_profile.get("display_name", "Anonymous"),
        role=role,
        compatibility_score=score,
        skills=[s.title() for s in list(candidate_skills)[:6]],
        complementary_skills=[s.title() for s in list(complementary)[:4]],
        shared_skills=[s.title() for s in list(shared)[:4]],
        missing_team_skills=[s.title() for s in list(missing_required)[:4]],
        shared_interests=[s.title() for s in list(shared_interests)[:3]],
        availability_overlap=avail_overlap,
        ai_reasoning=reasoning,
    )


def _infer_role(skills: set[str]) -> str:
    """Infer a team role from skills."""
    role_keywords = {
        "Frontend UI/UX": {"react", "vue", "angular", "figma", "css", "tailwind", "ui", "ux", "frontend"},
        "Backend Developer": {"node", "express", "django", "flask", "fastapi", "spring", "backend", "api"},
        "ML Engineer": {"machine learning", "ml", "tensorflow", "pytorch", "deep learning", "ai"},
        "Data Analyst": {"pandas", "numpy", "data analysis", "sql", "tableau", "data science"},
        "DevOps/Cloud": {"docker", "kubernetes", "aws", "gcp", "azure", "devops", "cloud", "ci/cd"},
        "Mobile Developer": {"flutter", "react native", "swift", "kotlin", "android", "ios"},
        "Full Stack": {"full stack", "fullstack"},
    }

    for role, keywords in role_keywords.items():
        if skills & keywords:
            return role

    return "General Developer"


# ── Planner Conflict Detection ────────────────────────────────

def detect_conflicts(
    events: list[dict],
) -> PlannerConflictResponse:
    """
    Detect scheduling conflicts between events.
    Checks for date overlaps, deadline collisions, and availability conflicts.
    """
    conflicts: list[PlannerConflict] = []

    parsed_events = []
    for ev in events:
        parsed_events.append(PlannerEvent(**ev) if isinstance(ev, dict) else ev)

    # Compare all pairs
    for i in range(len(parsed_events)):
        for j in range(i + 1, len(parsed_events)):
            ev_a = parsed_events[i]
            ev_b = parsed_events[j]

            conflict = _check_pair_conflict(ev_a, ev_b)
            if conflict:
                conflicts.append(conflict)

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    conflicts.sort(key=lambda c: severity_order.get(c.severity, 3))

    return PlannerConflictResponse(
        conflicts=conflicts,
        total_events=len(parsed_events),
        conflict_count=len(conflicts),
    )


def _check_pair_conflict(
    ev_a: PlannerEvent,
    ev_b: PlannerEvent,
) -> Optional[PlannerConflict]:
    """Check if two events conflict."""
    from datetime import datetime

    def parse_date(d: str) -> Optional[datetime]:
        for fmt in ("%Y-%m-%d", "%d %b %Y", "%d/%m/%Y", "%B %d, %Y"):
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                continue
        return None

    date_a = parse_date(ev_a.event_date)
    date_b = parse_date(ev_b.event_date)

    if not date_a or not date_b:
        return None

    end_a = parse_date(ev_a.end_date) if ev_a.end_date else date_a
    end_b = parse_date(ev_b.end_date) if ev_b.end_date else date_b

    # Check date overlap
    if date_a <= end_b and date_b <= end_a:
        # Determine severity
        if ev_a.event_type == "academic" or ev_b.event_type == "academic":
            severity = "high"
            description = f"'{ev_a.title}' overlaps with '{ev_b.title}' — academic event affected"
            suggestion = "Consider dropping the non-academic event or finding an alternative"
        elif date_a == date_b:
            severity = "medium"
            description = f"'{ev_a.title}' and '{ev_b.title}' fall on the same date"
            suggestion = "Check if time slots allow attending both"
        else:
            severity = "medium"
            description = f"'{ev_a.title}' overlaps with '{ev_b.title}'"
            suggestion = None

        return PlannerConflict(
            conflict_type="overlap",
            severity=severity,
            event_a=ev_a,
            event_b=ev_b,
            description=description,
            suggestion=suggestion,
        )

    # Check same-day deadline collision
    if date_a == date_b and ev_a.event_type != ev_b.event_type:
        return PlannerConflict(
            conflict_type="deadline_collision",
            severity="low",
            event_a=ev_a,
            event_b=ev_b,
            description=f"'{ev_a.title}' and '{ev_b.title}' have the same date",
            suggestion="Plan your time carefully for this date",
        )

    return None
