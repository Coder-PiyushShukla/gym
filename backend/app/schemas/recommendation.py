"""
DISHA Recommendation Schemas.
Covers matching, WHY THIS / WHY NOT, and skill gap analysis.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.opportunity import EligibilityStatus, OpportunityListItem


class MatchBreakdown(BaseModel):
    """Detailed matching score components (0-100 each)."""
    skill_match: float = 0
    interest_match: float = 0
    career_match: float = 0
    availability_match: float = 0
    budget_match: float = 0
    format_match: float = 0
    accessibility_match: float = 0


class SkillGap(BaseModel):
    """Skill gap analysis result."""
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    optional_skills: list[str] = []
    skill_gap_score: float = 0  # 0 = no gaps, 100 = all gaps


class RecommendationItem(BaseModel):
    """A single recommendation with full analysis."""
    opportunity: OpportunityListItem
    overall_score: int = 0
    match_breakdown: MatchBreakdown = Field(default_factory=MatchBreakdown)
    eligibility: EligibilityStatus = EligibilityStatus.UNKNOWN
    eligibility_reasons: list[str] = []
    trust_score: int = 0
    why_this: list[str] = []
    why_not: list[str] = []
    skill_gap: SkillGap = Field(default_factory=SkillGap)
    access_score: Optional[int] = None


class RecommendationRequest(BaseModel):
    """Request for generating recommendations."""
    user_id: Optional[str] = None
    limit: int = Field(default=10, le=50)
    include_expired: bool = False
    theme_filter: Optional[str] = None
    format_filter: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Full recommendation response."""
    items: list[RecommendationItem] = []
    total: int = 0
    profile_completeness: float = 0  # how complete the student profile is
