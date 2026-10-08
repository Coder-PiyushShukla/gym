"""
DISHA User & Profile Schemas.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str
    level: str = "intermediate"  # beginner | intermediate | advanced
    category: Optional[str] = None


class StudentProfile(BaseModel):
    """Student profile for matching and eligibility."""
    user_id: str
    display_name: Optional[str] = None
    academic_year: Optional[int] = None  # 1, 2, 3, 4
    degree_type: Optional[str] = None    # e.g., "B.Tech", "B.Sc"
    institution: Optional[str] = None
    career_goal: Optional[str] = None
    interests: list[str] = []
    availability: Optional[str] = None   # "weekends", "weekdays", "flexible"
    budget: Optional[str] = None         # "free", "low", "medium", "any"
    preferred_format: Optional[str] = None  # "remote", "in-person", "hybrid"
    location: Optional[str] = None
    experience_level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    sustainability_interest: bool = False
    skills: list[Skill] = []

    # Privacy settings
    allow_eligibility_check: bool = True
    allow_team_visibility: bool = True
    allow_external_scraping: bool = False


class StudentProfileUpdate(BaseModel):
    """Partial update for student profile."""
    display_name: Optional[str] = None
    academic_year: Optional[int] = None
    degree_type: Optional[str] = None
    institution: Optional[str] = None
    career_goal: Optional[str] = None
    interests: Optional[list[str]] = None
    availability: Optional[str] = None
    budget: Optional[str] = None
    preferred_format: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    sustainability_interest: Optional[bool] = None
    skills: Optional[list[Skill]] = None
    allow_eligibility_check: Optional[bool] = None
    allow_team_visibility: Optional[bool] = None
    allow_external_scraping: Optional[bool] = None


class ProfileResponse(BaseModel):
    """Profile data returned to frontend."""
    user_id: str
    display_name: Optional[str] = None
    academic_year: Optional[int] = None
    degree_type: Optional[str] = None
    institution: Optional[str] = None
    career_goal: Optional[str] = None
    interests: list[str] = []
    availability: Optional[str] = None
    budget: Optional[str] = None
    preferred_format: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    sustainability_interest: bool = False
    skills: list[Skill] = []
    allow_eligibility_check: bool = True
    allow_team_visibility: bool = True
    allow_external_scraping: bool = False
