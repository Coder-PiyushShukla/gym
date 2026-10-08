"""
DISHA Custom Exceptions.
Provides structured, API-friendly error types.
"""

from __future__ import annotations

from typing import Any, Optional


class DishaError(Exception):
    """Base exception for all DISHA errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(DishaError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(
            message=detail,
            code=f"{resource.upper().replace(' ', '_')}_NOT_FOUND",
            status_code=404,
        )


class ValidationError(DishaError):
    """Request validation failed."""

    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details or {},
        )


class AuthenticationError(DishaError):
    """Authentication required or failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_REQUIRED",
            status_code=401,
        )


class AuthorizationError(DishaError):
    """Insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class ExternalServiceError(DishaError):
    """External service (Gemini, source, etc.) failed."""

    def __init__(self, service: str = "external service", message: str = ""):
        detail = f"{service} is unavailable"
        if message:
            detail = f"{service}: {message}"
        super().__init__(
            message=detail,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service},
        )


class RateLimitError(DishaError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class IngestionError(DishaError):
    """Source ingestion pipeline error."""

    def __init__(self, source: str = "", message: str = "Ingestion failed"):
        super().__init__(
            message=message,
            code="INGESTION_ERROR",
            status_code=500,
            details={"source": source},
        )
