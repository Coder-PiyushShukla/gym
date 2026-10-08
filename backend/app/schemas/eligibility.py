"""
DISHA Eligibility Schemas.
Re-exported from opportunity for cleaner imports.
"""

from app.schemas.opportunity import (
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    EligibilityReason,
    EligibilityStatus,
    EligibilityStructured,
)

__all__ = [
    "EligibilityCheckRequest",
    "EligibilityCheckResponse",
    "EligibilityReason",
    "EligibilityStatus",
    "EligibilityStructured",
]
