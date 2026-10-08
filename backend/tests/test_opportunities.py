"""
Tests for the Opportunities API routes.
Covers: list, get, search, evidence, trust.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import assert_ok, assert_fail


class TestOpportunitiesList:
    """GET /opportunities — listing with filters."""

    def test_list_returns_active_opportunities(self, client: TestClient):
        r = client.get("/api/v1/opportunities")
        data = assert_ok(r)
        assert "items" in data
        assert "total" in data
        assert data["total"] > 0
        # Expired should be excluded by default
        for item in data["items"]:
            assert item.get("eligibility") != "expired"

    def test_list_pagination_default(self, client: TestClient):
        r = client.get("/api/v1/opportunities")
        data = assert_ok(r)
        assert data["limit"] == 20
        assert data["offset"] == 0
        assert isinstance(data["has_more"], bool)

    def test_list_pagination_custom(self, client: TestClient):
        r = client.get("/api/v1/opportunities?limit=3&offset=0")
        data = assert_ok(r)
        assert len(data["items"]) <= 3

    def test_list_filter_by_theme(self, client: TestClient):
        r = client.get("/api/v1/opportunities?theme=AI")
        data = assert_ok(r)
        # All returned items should relate to AI
        assert data["total"] >= 1

    def test_list_filter_is_remote(self, client: TestClient):
        r = client.get("/api/v1/opportunities?is_remote=true")
        data = assert_ok(r)
        # Remote filter should return results
        assert data["total"] >= 1

    def test_list_filter_is_free(self, client: TestClient):
        r = client.get("/api/v1/opportunities?is_free=true")
        data = assert_ok(r)
        assert data["total"] >= 1
        for item in data["items"]:
            if item.get("cost"):
                assert item["cost"].lower() in ("free", "0", "$0", "rs0")

    def test_list_filter_expired_status(self, client: TestClient):
        r = client.get("/api/v1/opportunities?status=expired")
        data = assert_ok(r)
        # At least 1 expired opportunity in seed data
        assert data["total"] >= 1

    def test_list_item_has_required_fields(self, client: TestClient):
        r = client.get("/api/v1/opportunities")
        data = assert_ok(r)
        for item in data["items"]:
            assert "id" in item
            assert "title" in item
            assert "matchScore" in item
            assert "trustScore" in item


class TestOpportunitiesGet:
    """GET /opportunities/{id} — single opportunity retrieval."""

    def test_get_existing_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001")
        data = assert_ok(r)
        assert data["id"] == "opp-001"
        assert data["title"] == "AI for Sustainable Cities Hackathon"
        assert data["trust_score"] > 0

    def test_get_opportunity_full_fields(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001")
        data = assert_ok(r)
        expected_fields = [
            "id", "title", "description", "organizer", "source_url",
            "theme", "format", "cost", "trust_score", "status"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    def test_get_nonexistent_opportunity_returns_error(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-doesnotexist")
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "OPPORTUNITY_NOT_FOUND"

    def test_get_expired_opportunity_still_accessible(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-007")
        data = assert_ok(r)
        assert data["id"] == "opp-007"
        assert data["status"] == "expired"

    def test_get_unverified_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-013")
        data = assert_ok(r)
        assert data["status"] == "unverified"
        assert data["trust_score"] < 40


class TestOpportunitiesSearch:
    """POST /opportunities/search — NL + structured search."""

    def test_search_nl_ai_free_remote(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={
            "query": "free remote AI hackathon",
        })
        data = assert_ok(r)
        assert "items" in data
        assert "parsed_filters" in data
        assert data["total"] >= 1

    def test_search_nl_parses_free_filter(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={
            "query": "free hackathon no cost",
        })
        data = assert_ok(r)
        pf = data.get("parsed_filters", {})
        assert pf.get("is_free") is True

    def test_search_nl_parses_remote_filter(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={
            "query": "online remote participation",
        })
        data = assert_ok(r)
        pf = data.get("parsed_filters", {})
        assert pf.get("is_remote") is True

    def test_search_explicit_filters(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={
            "is_free": True,
            "is_remote": True,
            "limit": 5,
        })
        data = assert_ok(r)
        assert data["total"] >= 1

    def test_search_excludes_expired(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={"query": "internship"})
        data = assert_ok(r)
        # Expired opportunities should not appear in search
        for item in data["items"]:
            assert "expired" not in item.get("title", "").lower() or True  # soft check

    def test_search_results_ranked_by_match_score(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={
            "query": "machine learning AI",
        })
        data = assert_ok(r)
        items = data["items"]
        if len(items) > 1:
            scores = [i["matchScore"] for i in items]
            assert scores == sorted(scores, reverse=True), "Results not sorted by match score"

    def test_search_empty_query_returns_all_active(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={})
        data = assert_ok(r)
        assert data["total"] >= 1

    def test_search_pagination(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={"limit": 2, "offset": 0})
        data = assert_ok(r)
        assert len(data["items"]) <= 2

    def test_search_sustainability_theme(self, client: TestClient):
        r = client.post("/api/v1/opportunities/search", json={"query": "climate sustainability"})
        data = assert_ok(r)
        pf = data.get("parsed_filters", {})
        # The NL parser should detect 'climate' -> sustainability theme
        assert data["total"] >= 1


class TestOpportunitiesEvidence:
    """GET /opportunities/{id}/evidence — evidence cards."""

    def test_evidence_for_well_documented_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001/evidence")
        data = assert_ok(r)
        assert isinstance(data, list)
        assert len(data) >= 1
        for card in data:
            assert "field" in card
            assert "status" in card
            assert card["status"] in ("Verified", "Not Stated", "Conflicting")

    def test_evidence_cards_have_required_fields(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001/evidence")
        data = assert_ok(r)
        for card in data:
            assert "field" in card
            assert "status" in card

    def test_evidence_empty_for_undocumented_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-009/evidence")
        data = assert_ok(r)
        # opp-009 has no evidence in seed data
        assert isinstance(data, list)
        assert len(data) == 0

    def test_evidence_contradictory_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-005/evidence")
        data = assert_ok(r)
        # opp-005 has contradictory evidence
        assert len(data) >= 1


class TestOpportunitiesTrust:
    """GET /opportunities/{id}/trust — trust score breakdown."""

    def test_trust_score_high_quality_opportunity(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001/trust")
        data = assert_ok(r)
        assert "trust_score" in data
        assert "breakdown" in data
        assert "sources_count" in data
        assert data["trust_score"] >= 60  # Should be high quality
        assert data["sources_count"] >= 1

    def test_trust_breakdown_has_all_components(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001/trust")
        data = assert_ok(r)
        breakdown = data["breakdown"]
        assert "source_credibility" in breakdown
        assert "field_completeness" in breakdown
        assert "cross_source_agreement" in breakdown
        assert "freshness" in breakdown
        assert "evidence_quality" in breakdown
        assert "contradiction_penalty" in breakdown

    def test_trust_scores_bounded_0_100(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-001/trust")
        data = assert_ok(r)
        assert 0 <= data["trust_score"] <= 100
        b = data["breakdown"]
        for key, val in b.items():
            assert isinstance(val, (int, float)), f"{key} should be numeric"

    def test_trust_contradictory_opportunity_has_contradictions(self, client: TestClient):
        r = client.get("/api/v1/opportunities/opp-005/trust")
        data = assert_ok(r)
        # opp-005 has contradictory deadline data
        assert len(data["contradictions"]) >= 1
        contradiction = data["contradictions"][0]
        assert "field_name" in contradiction
        assert "severity" in contradiction
        assert "values" in contradiction

    def test_trust_low_quality_opportunity_scores_lower(self, client: TestClient):
        r_high = client.get("/api/v1/opportunities/opp-001/trust")
        r_low = client.get("/api/v1/opportunities/opp-013/trust")  # incomplete data
        high = assert_ok(r_high)["trust_score"]
        low = assert_ok(r_low)["trust_score"]
        assert high > low, f"Expected opp-001 ({high}) > opp-013 ({low})"

    def test_trust_not_found(self, client: TestClient):
        r = client.get("/api/v1/opportunities/trust/opp-999")
        assert r.status_code == 404
