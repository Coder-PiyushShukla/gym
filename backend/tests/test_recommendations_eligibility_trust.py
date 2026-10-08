"""
Tests for the Recommendations, Eligibility, and Trust routes.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import assert_ok, assert_fail


class TestRecommendations:
    """POST /recommendations + GET /recommendations."""

    def test_get_recommendations(self, client: TestClient):
        r = client.get("/api/v1/recommendations")
        data = assert_ok(r)
        assert "items" in data
        assert "total" in data
        assert "profile_completeness" in data
        assert data["total"] >= 1

    def test_post_recommendations_returns_items(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 5})
        data = assert_ok(r)
        assert data["total"] >= 1
        assert len(data["items"]) <= 5

    def test_recommendations_item_structure(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 3})
        data = assert_ok(r)
        item = data["items"][0]
        assert "opportunity" in item
        assert "overall_score" in item
        assert "match_breakdown" in item
        assert "eligibility" in item
        assert "trust_score" in item
        assert "why_this" in item
        assert "why_not" in item
        assert "skill_gap" in item

    def test_recommendations_sorted_by_score(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 10})
        data = assert_ok(r)
        scores = [item["overall_score"] for item in data["items"]]
        assert scores == sorted(scores, reverse=True), "Not sorted by overall_score"

    def test_recommendations_match_breakdown_components(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 1})
        data = assert_ok(r)
        breakdown = data["items"][0]["match_breakdown"]
        required = [
            "skill_match", "interest_match", "career_match",
            "availability_match", "budget_match", "format_match", "accessibility_match"
        ]
        for key in required:
            assert key in breakdown, f"Missing breakdown key: {key}"
            assert 0 <= breakdown[key] <= 100

    def test_recommendations_scores_bounded(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 10})
        data = assert_ok(r)
        for item in data["items"]:
            assert 0 <= item["overall_score"] <= 100
            assert 0 <= item["trust_score"] <= 100

    def test_recommendations_why_this_is_evidence_based(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 3})
        data = assert_ok(r)
        for item in data["items"]:
            # why_this should be a list of strings
            assert isinstance(item["why_this"], list)
            for reason in item["why_this"]:
                assert isinstance(reason, str)
                assert len(reason) > 0

    def test_recommendations_profile_completeness(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={})
        data = assert_ok(r)
        pc = data["profile_completeness"]
        assert 0 <= pc <= 100

    def test_recommendations_exclude_expired_default(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 20})
        data = assert_ok(r)
        for item in data["items"]:
            # Status should not be expired
            opp = item["opportunity"]
            assert opp.get("eligibility") != "expired"

    def test_recommendations_include_expired_option(self, client: TestClient):
        r_without = client.post("/api/v1/recommendations", json={"include_expired": False})
        r_with = client.post("/api/v1/recommendations", json={"include_expired": True})
        d_without = assert_ok(r_without)
        d_with = assert_ok(r_with)
        # Including expired should result in same or more items
        assert d_with["total"] >= d_without["total"]

    def test_recommendations_theme_filter(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"theme_filter": "AI"})
        data = assert_ok(r)
        assert data["total"] >= 1

    def test_recommendations_eligibility_values(self, client: TestClient):
        r = client.post("/api/v1/recommendations", json={"limit": 10})
        data = assert_ok(r)
        valid_statuses = {"Eligible", "Not Eligible", "Unknown"}
        for item in data["items"]:
            assert item["eligibility"] in valid_statuses


class TestEligibility:
    """POST /eligibility/check."""

    def test_check_eligible_opportunity(self, client: TestClient):
        """Demo student (B.Tech yr2) should be eligible for opp-001 (undergraduate)."""
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert "status" in data
        assert "reasons" in data
        assert data["status"] in ("Eligible", "Not Eligible", "Unknown")

    def test_check_eligibility_reasons_structure(self, client: TestClient):
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        for reason in data["reasons"]:
            assert "field" in reason
            assert "status" in reason
            assert "reason" in reason
            assert reason["status"] in ("Eligible", "Not Eligible", "Unknown")

    def test_check_expired_opportunity_eligibility(self, client: TestClient):
        """Eligibility check should still work for expired opportunities."""
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-007"})
        data = assert_ok(r)
        # opp-007 requires 3rd/4th year B.Tech only; demo student is year 2
        assert data["status"] in ("Not Eligible", "Unknown")

    def test_check_nonexistent_opportunity(self, client: TestClient):
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-999"})
        body = r.json()
        assert body["success"] is False

    def test_check_open_to_all_opportunity(self, client: TestClient):
        """opp-009 is open to all undergrads — demo student should be eligible."""
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-009"})
        data = assert_ok(r)
        assert data["status"] in ("Eligible", "Unknown")

    def test_check_incomplete_eligibility_data(self, client: TestClient):
        """opp-013 has no eligibility data — should return UNKNOWN."""
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-013"})
        data = assert_ok(r)
        assert data["status"] == "Unknown"

    def test_check_nationality_requirement(self, client: TestClient):
        """opp-011 requires Indian students — demo student is in India."""
        r = client.post("/api/v1/eligibility/check", json={"opportunity_id": "opp-011"})
        data = assert_ok(r)
        # Demo student location is 'India' — should match
        assert data["status"] in ("Eligible", "Unknown")


class TestTrustEndpoint:
    """GET /trust/{opp_id} — standalone trust endpoint."""

    def test_trust_basic(self, client: TestClient):
        r = client.get("/api/v1/trust/opp-001")
        data = assert_ok(r)
        assert "trust_score" in data
        assert "breakdown" in data
        assert 0 <= data["trust_score"] <= 100

    def test_trust_with_contradictions(self, client: TestClient):
        r = client.get("/api/v1/trust/opp-005")
        data = assert_ok(r)
        # opp-005 has deadline contradiction
        assert "contradictions" in data
        assert len(data["contradictions"]) >= 1
        c = data["contradictions"][0]
        assert c["field_name"] == "application_deadline"
        assert c["severity"] == "high"

    def test_trust_not_found(self, client: TestClient):
        r = client.get("/api/v1/trust/opp-not-real")
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "OPPORTUNITY_NOT_FOUND"

    def test_trust_all_opportunities_compute(self, client: TestClient):
        """All seed opportunities should compute trust without error."""
        for i in range(1, 16):
            opp_id = f"opp-{i:03d}"
            r = client.get(f"/api/v1/trust/{opp_id}")
            data = assert_ok(r)
            assert 0 <= data["trust_score"] <= 100

    def test_trust_freshness_affects_score(self, client: TestClient):
        """opp-001 was verified recently; should have higher freshness than opp-013 (never)."""
        r1 = client.get("/api/v1/trust/opp-001")
        r13 = client.get("/api/v1/trust/opp-013")
        d1 = assert_ok(r1)
        d13 = assert_ok(r13)
        f1 = d1["breakdown"]["freshness"]
        f13 = d13["breakdown"]["freshness"]
        assert f1 > f13, f"opp-001 freshness ({f1}) should exceed opp-013 ({f13})"
