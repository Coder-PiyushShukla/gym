"""
DISHA Matching Service.
Computes personalized opportunity scores using deterministic + semantic matching.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.logging import get_logger
from app.schemas.recommendation import MatchBreakdown, SkillGap

logger = get_logger("matching_service")

# Weight each matching component
MATCH_WEIGHTS = {
    "skill": 0.25,
    "interest": 0.15,
    "career": 0.15,
    "availability": 0.10,
    "budget": 0.10,
    "format": 0.10,
    "accessibility": 0.15,
}


def _normalize_skill(skill: str) -> str:
    """Normalize a skill name for comparison."""
    return skill.strip().lower().replace("-", " ").replace("_", " ")


def compute_skill_match(
    student_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str] = [],
) -> tuple[float, SkillGap]:
    """
    Compute skill matching score and identify gaps.
    Returns (score 0-100, SkillGap).
    """
    if not required_skills and not preferred_skills:
        return 80.0, SkillGap(skill_gap_score=0)  # No requirements = broadly accessible

    student_normalized = {_normalize_skill(s) for s in student_skills}

    required_normalized = {_normalize_skill(s) for s in required_skills}
    preferred_normalized = {_normalize_skill(s) for s in preferred_skills}

    # Fuzzy matching: check if any student skill contains or is contained by required skill
    matched_required = set()
    for req in required_normalized:
        for stu in student_normalized:
            if req in stu or stu in req or _fuzzy_skill_match(stu, req):
                matched_required.add(req)
                break

    matched_preferred = set()
    for pref in preferred_normalized:
        for stu in student_normalized:
            if pref in stu or stu in pref or _fuzzy_skill_match(stu, pref):
                matched_preferred.add(pref)
                break

    missing_required = required_normalized - matched_required
    missing_preferred = preferred_normalized - matched_preferred - matched_required

    # Score calculation
    if required_normalized:
        required_ratio = len(matched_required) / len(required_normalized)
        score = required_ratio * 80  # Required skills worth 80%
    else:
        score = 80

    if preferred_normalized:
        preferred_ratio = len(matched_preferred) / len(preferred_normalized)
        score += preferred_ratio * 20  # Preferred skills worth 20%
    else:
        score += 20  # Full bonus if no preferred specified

    # Build SkillGap
    gap_score = (len(missing_required) / max(len(required_normalized), 1)) * 100 if required_normalized else 0

    skill_gap = SkillGap(
        matched_skills=[_title_case(s) for s in (matched_required | matched_preferred)],
        missing_skills=[_title_case(s) for s in missing_required],
        optional_skills=[_title_case(s) for s in missing_preferred],
        skill_gap_score=round(gap_score, 1),
    )

    return min(100, round(score, 1)), skill_gap


def _fuzzy_skill_match(skill_a: str, skill_b: str) -> bool:
    """Simple fuzzy matching for skill names."""
    # Handle common abbreviations
    ALIASES = {
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "ds": "data science",
        "devops": "dev ops",
        "ui": "user interface",
        "ux": "user experience",
        "ui/ux": "user interface",
        "react.js": "react",
        "node.js": "node",
        "next.js": "next",
        "vue.js": "vue",
    }
    a = ALIASES.get(skill_a, skill_a)
    b = ALIASES.get(skill_b, skill_b)
    return a == b or a in b or b in a


def _title_case(s: str) -> str:
    """Convert skill back to title case."""
    return " ".join(word.capitalize() for word in s.split())


def compute_interest_match(
    student_interests: list[str],
    opportunity_theme: Optional[str],
    opportunity_tags: list[str] = [],
) -> float:
    """Match student interests against opportunity theme/tags."""
    if not student_interests:
        return 50.0  # Neutral if no interests specified

    all_opp_tags = []
    if opportunity_theme:
        all_opp_tags.append(opportunity_theme.lower())
    all_opp_tags.extend(t.lower() for t in opportunity_tags)

    if not all_opp_tags:
        return 50.0

    student_lower = [i.lower() for i in student_interests]

    matches = 0
    for interest in student_lower:
        for tag in all_opp_tags:
            if interest in tag or tag in interest:
                matches += 1
                break

    return min(100, (matches / len(student_lower)) * 100)


def compute_career_match(
    career_goal: Optional[str],
    opportunity_theme: Optional[str],
    required_skills: list[str] = [],
) -> float:
    """Match career goal against opportunity theme and skills."""
    if not career_goal:
        return 50.0

    goal_lower = career_goal.lower()
    score = 0
    checks = 0

    if opportunity_theme:
        checks += 1
        theme_lower = opportunity_theme.lower()
        goal_words = goal_lower.split()
        theme_words = theme_lower.split()
        overlap = sum(1 for w in goal_words if any(w in tw for tw in theme_words))
        if overlap > 0:
            score += min(100, overlap * 40)

    if required_skills:
        checks += 1
        skill_text = " ".join(s.lower() for s in required_skills)
        goal_words = goal_lower.replace("/", " ").split()
        overlap = sum(1 for w in goal_words if w in skill_text)
        if overlap > 0:
            score += min(100, overlap * 30)

    return min(100, score / max(checks, 1))


def compute_availability_match(
    student_availability: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    format_type: Optional[str],
) -> float:
    """Check if timing works for the student."""
    if not student_availability:
        return 60.0

    avail_lower = student_availability.lower()

    if avail_lower == "flexible":
        return 95.0

    # Weekend events are great for "weekends" availability
    if avail_lower == "weekends":
        if format_type and "remote" in format_type.lower():
            return 90.0  # Remote + weekends is very compatible
        return 70.0

    if avail_lower == "weekdays":
        return 70.0

    return 60.0


def compute_budget_match(
    student_budget: Optional[str],
    opportunity_cost: Optional[str],
) -> float:
    """Check if the opportunity fits the student's budget."""
    if not opportunity_cost:
        return 60.0  # Unknown cost

    cost_lower = opportunity_cost.lower().strip()

    if cost_lower in ("free", "0", "$0", "₹0", "no cost"):
        return 100.0  # Free is always good

    if not student_budget:
        return 50.0

    budget_lower = student_budget.lower()

    if budget_lower == "any":
        return 95.0
    elif budget_lower == "free":
        if cost_lower == "free":
            return 100.0
        return 10.0  # Student wants free but it costs money
    elif budget_lower == "low":
        # Try to extract numeric cost
        try:
            cost_num = float("".join(c for c in cost_lower if c.isdigit() or c == "."))
            return 90.0 if cost_num < 1000 else 40.0
        except (ValueError, TypeError):
            return 50.0
    elif budget_lower == "medium":
        return 70.0

    return 50.0


def compute_format_match(
    student_preference: Optional[str],
    opportunity_format: Optional[str],
) -> float:
    """Check if the format matches student preference."""
    if not student_preference or not opportunity_format:
        return 60.0

    pref_lower = student_preference.lower()
    fmt_lower = opportunity_format.lower()

    if "remote" in pref_lower and ("remote" in fmt_lower or "online" in fmt_lower):
        return 100.0
    elif "in-person" in pref_lower and "in-person" in fmt_lower:
        return 100.0
    elif "hybrid" in pref_lower:
        return 85.0  # Hybrid students are flexible
    elif "remote" in pref_lower and "hybrid" in fmt_lower:
        return 70.0  # Hybrid has remote option
    elif "remote" in pref_lower and "in-person" in fmt_lower:
        return 20.0  # Format mismatch

    return 60.0


def compute_accessibility_score(opportunity: dict) -> float:
    """
    Compute access/equity score.
    Factors: cost, remote, time commitment, beginner friendliness.
    """
    score = 50.0  # Base

    cost = (opportunity.get("cost") or "").lower()
    if cost in ("free", "0", "$0", "₹0"):
        score += 20
    elif cost:
        score += 5

    fmt = (opportunity.get("format") or "").lower()
    if "remote" in fmt or "online" in fmt:
        score += 15
    elif "hybrid" in fmt:
        score += 10

    exp = (opportunity.get("experience_level") or "").lower()
    if "beginner" in exp or "any" in exp:
        score += 10
    elif "intermediate" in exp:
        score += 5

    is_remote = opportunity.get("is_remote")
    if is_remote:
        score += 5

    return min(100, score)


def compute_full_match(
    student_profile: dict,
    opportunity: dict,
) -> tuple[int, MatchBreakdown, SkillGap]:
    """
    Compute the full match score and breakdown.
    Returns (overall_score, breakdown, skill_gap).
    """
    student_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in student_profile.get("skills", [])
    ]

    skill_score, skill_gap = compute_skill_match(
        student_skills=student_skills,
        required_skills=opportunity.get("required_skills", []),
        preferred_skills=opportunity.get("preferred_skills", []),
    )

    interest_score = compute_interest_match(
        student_interests=student_profile.get("interests", []),
        opportunity_theme=opportunity.get("theme"),
        opportunity_tags=opportunity.get("sustainability_tags", []),
    )

    career_score = compute_career_match(
        career_goal=student_profile.get("career_goal"),
        opportunity_theme=opportunity.get("theme"),
        required_skills=opportunity.get("required_skills", []),
    )

    availability_score = compute_availability_match(
        student_availability=student_profile.get("availability"),
        start_date=opportunity.get("start_date"),
        end_date=opportunity.get("end_date"),
        format_type=opportunity.get("format"),
    )

    budget_score = compute_budget_match(
        student_budget=student_profile.get("budget"),
        opportunity_cost=opportunity.get("cost"),
    )

    format_score = compute_format_match(
        student_preference=student_profile.get("preferred_format"),
        opportunity_format=opportunity.get("format"),
    )

    accessibility_score = compute_accessibility_score(opportunity)

    breakdown = MatchBreakdown(
        skill_match=round(skill_score, 1),
        interest_match=round(interest_score, 1),
        career_match=round(career_score, 1),
        availability_match=round(availability_score, 1),
        budget_match=round(budget_score, 1),
        format_match=round(format_score, 1),
        accessibility_match=round(accessibility_score, 1),
    )

    # Weighted overall score
    overall = (
        MATCH_WEIGHTS["skill"] * skill_score
        + MATCH_WEIGHTS["interest"] * interest_score
        + MATCH_WEIGHTS["career"] * career_score
        + MATCH_WEIGHTS["availability"] * availability_score
        + MATCH_WEIGHTS["budget"] * budget_score
        + MATCH_WEIGHTS["format"] * format_score
        + MATCH_WEIGHTS["accessibility"] * accessibility_score
    )

    overall_score = max(0, min(100, int(round(overall))))

    logger.info(
        "match_computed",
        overall=overall_score,
        skill=skill_score,
        career=career_score,
    )

    return overall_score, breakdown, skill_gap
