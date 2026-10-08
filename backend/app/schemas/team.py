"""
DISHA Team Schemas.
Team matching and complementary skill analysis.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TeamMatchCandidate(BaseModel):
    """A teammate recommendation with complementary analysis."""
    user_id: str
    display_name: str
    role: Optional[str] = None
    compatibility_score: int = 0
    skills: list[str] = []
    complementary_skills: list[str] = []  # skills they have that student doesn't
    shared_skills: list[str] = []
    missing_team_skills: list[str] = []
    shared_interests: list[str] = []
    availability_overlap: Optional[str] = None
    ai_reasoning: str = ""  # WHY this teammate


class TeamMatchRequest(BaseModel):
    """Request for team matching."""
    opportunity_id: str
    user_id: Optional[str] = None
    target_team_size: int = Field(default=4, ge=2, le=10)


class TeamMatchResponse(BaseModel):
    """Team matching response."""
    opportunity_id: str
    opportunity_title: str
    user_role: Optional[str] = None
    candidates: list[TeamMatchCandidate] = []
    team_coverage: Optional[dict[str, bool]] = None  # skill → covered?


# ── Planner ───────────────────────────────────────────────────

class PlannerEvent(BaseModel):
    """An event in the student's planner."""
    id: Optional[str] = None
    user_id: str
    title: str
    event_type: str  # "opportunity", "academic", "learning", "personal"
    event_date: str
    end_date: Optional[str] = None
    time: Optional[str] = None
    opportunity_id: Optional[str] = None
    notes: Optional[str] = None


class PlannerConflict(BaseModel):
    """A detected scheduling conflict."""
    conflict_type: str  # "overlap", "deadline_collision", "availability"
    severity: str  # "high", "medium", "low"
    event_a: PlannerEvent
    event_b: PlannerEvent
    description: str
    suggestion: Optional[str] = None


class PlannerConflictRequest(BaseModel):
    """Request for conflict detection."""
    user_id: Optional[str] = None
    include_opportunities: bool = True


class PlannerConflictResponse(BaseModel):
    """Conflict detection results."""
    conflicts: list[PlannerConflict] = []
    total_events: int = 0
    conflict_count: int = 0
