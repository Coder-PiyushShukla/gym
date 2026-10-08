"""
DISHA Roadmap Schemas.
Learning roadmap / readiness pathway for skill gaps.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RoadmapStep(BaseModel):
    """A single step in a readiness roadmap."""
    step_order: int
    skill: str
    learning_resource: Optional[str] = None
    resource_url: Optional[str] = None
    difficulty: str = "beginner"  # beginner | intermediate | advanced
    estimated_hours: Optional[float] = None
    reason: Optional[str] = None
    is_verified: bool = False  # whether the resource URL was verified


class RoadmapGenerateRequest(BaseModel):
    """Request to generate a readiness roadmap."""
    opportunity_id: str
    user_id: Optional[str] = None


class RoadmapResponse(BaseModel):
    """Full roadmap response."""
    id: str
    opportunity_id: str
    opportunity_title: str
    user_id: Optional[str] = None
    target_skills: list[str] = []
    current_skills: list[str] = []
    gap_skills: list[str] = []
    steps: list[RoadmapStep] = []
    total_estimated_hours: Optional[float] = None
    created_at: Optional[str] = None
