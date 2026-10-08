"""
DISHA Opportunity Schemas.
Pydantic v2 models for opportunity data at every pipeline stage.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class OpportunityFormat(str, Enum):
    ONLINE = "Online / Remote"
    IN_PERSON = "In-Person"
    HYBRID = "Hybrid"


class OpportunityStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DRAFT = "draft"
    UNVERIFIED = "unverified"


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ANY = "any"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "Eligible"
    NOT_ELIGIBLE = "Not Eligible"
    UNKNOWN = "Unknown"


# ── Evidence ──────────────────────────────────────────────────

class EvidenceSnippet(BaseModel):
    """A single piece of evidence grounding an extracted field."""
    field_name: str
    extracted_value: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    snippet: Optional[str] = None
    extracted_at: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EvidenceResponse(BaseModel):
    """Evidence card as displayed in the Trust drawer."""
    field: str
    value: Optional[str] = None
    source: Optional[str] = None
    status: str = "Not Stated"  # "Verified" | "Not Stated" | "Conflicting"


# ── Contradiction ─────────────────────────────────────────────

class Contradiction(BaseModel):
    """Detected contradiction between sources."""
    field_name: str
    values: list[dict[str, Any]]  # [{source, value}, ...]
    severity: str = "medium"  # low | medium | high


# ── Trust Score ───────────────────────────────────────────────

class TrustBreakdown(BaseModel):
    """Explainable trust score components (0-100 each)."""
    source_credibility: float = 0
    field_completeness: float = 0
    cross_source_agreement: float = 0
    freshness: float = 0
    evidence_quality: float = 0
    contradiction_penalty: float = 0


class TrustScoreResponse(BaseModel):
    """Trust score with full breakdown."""
    trust_score: int = 0
    breakdown: TrustBreakdown = Field(default_factory=TrustBreakdown)
    sources_count: int = 0
    last_verified_at: Optional[str] = None
    contradictions: list[Contradiction] = []


# ── Eligibility ───────────────────────────────────────────────

class EligibilityStructured(BaseModel):
    """Structured eligibility requirements parsed from source text."""
    academic_year: Optional[list[str]] = None
    degree_type: Optional[list[str]] = None
    age_range: Optional[dict[str, int]] = None  # {min, max}
    nationality: Optional[list[str]] = None
    gender: Optional[str] = None
    custom_requirements: list[str] = []


class EligibilityCheckRequest(BaseModel):
    """Request body for checking eligibility."""
    opportunity_id: str
    user_id: Optional[str] = None


class EligibilityReason(BaseModel):
    field: str
    status: EligibilityStatus
    reason: str


class EligibilityCheckResponse(BaseModel):
    status: EligibilityStatus
    reasons: list[EligibilityReason] = []


# ── SDG Tags ──────────────────────────────────────────────────

class SDGTag(BaseModel):
    sdg_id: int
    label: str
    reason: Optional[str] = None
    evidence: Optional[str] = None


# ── Core Opportunity ──────────────────────────────────────────

class OpportunityBase(BaseModel):
    """Fields shared across create/update/response."""
    title: Optional[str] = None
    description: Optional[str] = None
    organizer: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    theme: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    application_deadline: Optional[str] = None
    format: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    cost: Optional[str] = None
    currency: Optional[str] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    eligibility_text: Optional[str] = None
    eligibility_structured: Optional[EligibilityStructured] = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    experience_level: Optional[str] = None
    sustainability_tags: list[str] = []
    sdg_tags: list[SDGTag] = []
    application_url: Optional[str] = None
    status: OpportunityStatus = OpportunityStatus.ACTIVE
    trust_score: int = 0
    access_score: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating a new opportunity (admin/ingestion)."""
    title: str
    source_url: str


class OpportunityResponse(OpportunityBase):
    """Full opportunity response returned by the API."""
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_verified_at: Optional[str] = None
    sources_count: int = 0


class OpportunityListItem(BaseModel):
    """Compact opportunity for list views (Explore, Dashboard)."""
    id: str
    title: str
    organizer: Optional[str] = None
    matchScore: int = 0
    trustScore: int = 0
    eligibility: str = "Unknown"
    cost: Optional[str] = None
    format: Optional[str] = None
    deadline: Optional[str] = None
    sustainability: Optional[str] = None
    teamSize: Optional[str] = None
    lastVerified: Optional[str] = None
    sources: int = 0
    whyThis: list[str] = []
    whyNot: list[str] = []
    skillGaps: list[str] = []


class OpportunitySearchRequest(BaseModel):
    """Search request — supports natural language + structured filters."""
    query: Optional[str] = None
    theme: Optional[str] = None
    format: Optional[str] = None
    is_remote: Optional[bool] = None
    max_cost: Optional[float] = None
    experience_level: Optional[str] = None
    is_free: Optional[bool] = None
    sdg_ids: list[int] = []
    skills: list[str] = []
    limit: int = Field(default=20, le=100)
    offset: int = 0


class OpportunitySearchResponse(BaseModel):
    """Search results with parsed intent."""
    items: list[OpportunityListItem] = []
    total: int = 0
    parsed_filters: Optional[dict[str, Any]] = None
    has_more: bool = False
