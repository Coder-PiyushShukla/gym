"""
DISHA API Response Envelope.
Consistent response structure for all API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata attached to every API response."""
    request_id: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    data: Optional[T] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    error: Optional[dict[str, Any]] = None

    @classmethod
    def ok(cls, data: Any, request_id: str = "") -> "ApiResponse":
        return cls(
            success=True,
            data=data,
            meta=ResponseMeta(request_id=request_id),
        )

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        request_id: str = "",
        status_code: int = 500,
    ) -> "ApiResponse":
        return cls(
            success=False,
            data=None,
            meta=ResponseMeta(request_id=request_id),
            error={"code": code, "message": message},
        )


class PaginatedData(BaseModel, Generic[T]):
    """Wrapper for paginated list responses."""
    items: list[T] = []
    total: int = 0
    limit: int = 20
    offset: int = 0
    has_more: bool = False
