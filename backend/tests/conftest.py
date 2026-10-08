"""
DISHA Backend Test Configuration.
Shared fixtures and client setup for all tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Synchronous test client for the FastAPI app."""
    with TestClient(app, base_url="http://testserver") as c:
        yield c


# ── Convenience helpers ───────────────────────────────────────

def assert_ok(response, *, status: int = 200) -> dict:
    """Assert the response is successful and return parsed data."""
    assert response.status_code == status, (
        f"Expected {status}, got {response.status_code}: {response.text[:500]}"
    )
    body = response.json()
    assert body["success"] is True, f"Expected success=true, got: {body}"
    return body["data"]


def assert_fail(response, *, status: int = 404) -> dict:
    """Assert the response is an error and return the error dict."""
    assert response.status_code == status, (
        f"Expected {status}, got {response.status_code}: {response.text[:200]}"
    )
    body = response.json()
    assert body["success"] is False
    return body["error"]
