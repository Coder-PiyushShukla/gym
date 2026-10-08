"""
DISHA Backend — Main FastAPI Application.
Wires up routers, middleware, exception handlers, and rate limiting.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter
from slowapi.util import get_remote_address

from app.api.routes import (
    admin,
    eligibility,
    opportunities,
    recommendations,
    roadmap,
    teams,
    trust,
    users,
)
from app.core.config import get_settings
from app.core.exceptions import DishaError
from app.core.logging import get_logger, request_id_ctx, setup_logging

settings = get_settings()

# Setup structured logging
setup_logging(log_level=settings.log_level, json_format=settings.is_production)
logger = get_logger("app")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    logger.info("startup", app_name=settings.app_name, version=settings.app_version)
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DISHA Agentic AI Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ──────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def structlog_middleware(request: Request, call_next):
    """Inject request ID and log timing."""
    from app.core.logging import generate_request_id
    
    req_id = request.headers.get("x-request-id") or generate_request_id()
    request_id_ctx.set(req_id)
    
    start_time = time.perf_counter()
    
    # Pass request ID in response header
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )
        response.headers["X-Request-ID"] = req_id
        return response
    except Exception as exc:
        process_time = time.perf_counter() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(exc),
            process_time=round(process_time, 4),
            exc_info=True,
        )
        raise


# ── Exception Handlers ──────────────────────────────────────────

@app.exception_handler(DishaError)
async def disha_exception_handler(request: Request, exc: DishaError):
    """Handle custom application errors."""
    from app.schemas.common import ApiResponse
    req_id = request_id_ctx.get("")
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.fail(
            code=exc.code,
            message=exc.message,
            request_id=req_id,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    from app.schemas.common import ApiResponse
    req_id = request_id_ctx.get("")
    return JSONResponse(
        status_code=422,
        content=ApiResponse.fail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=req_id,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    from app.schemas.common import ApiResponse
    req_id = request_id_ctx.get("")
    
    # Don't leak internals in production
    msg = "An unexpected error occurred" if settings.is_production else str(exc)
    
    return JSONResponse(
        status_code=500,
        content=ApiResponse.fail(
            code="INTERNAL_ERROR",
            message=msg,
            request_id=req_id,
        ).model_dump(),
    )


# ── Routers ─────────────────────────────────────────────────────

api_v1 = FastAPI(title="API v1")

api_v1.include_router(opportunities.router)
api_v1.include_router(recommendations.router)
api_v1.include_router(eligibility.router)
api_v1.include_router(trust.router)
api_v1.include_router(roadmap.router)
api_v1.include_router(teams.teams_router)
api_v1.include_router(teams.planner_router)
api_v1.include_router(users.router)
api_v1.include_router(admin.router)


@app.get("/api/v1/health")
async def health_check():
    """System health endpoint."""
    return {
        "status": "healthy",
        "services": {
            "database": "healthy" if settings.has_supabase else "not_configured (demo mode)",
            "gemini": "healthy" if settings.has_gemini else "not_configured",
        }
    }


# Mount the API v1 to the main app
app.mount("/api/v1", api_v1)
