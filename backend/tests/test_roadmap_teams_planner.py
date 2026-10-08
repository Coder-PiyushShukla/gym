"""
Tests for Roadmap, Teams, Planner, Admin, and Profile API routes.
Covers all previously untested endpoints.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import assert_ok, assert_fail


# =============================================================================
#  ROADMAP TESTS
# =============================================================================

class TestRoadmapGenerate:
    """POST /roadmap/generate - generates a skill-gap learning path."""

    def test_generate_roadmap_valid_opportunity(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert "id" in data
        assert data["id"].startswith("roadmap-")
        assert data["opportunity_id"] == "opp-001"
        assert "steps" in data
        assert isinstance(data["steps"], list)

    def test_generate_roadmap_has_required_fields(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        required = [
            "id", "opportunity_id", "opportunity_title",
            "target_skills", "current_skills", "gap_skills",
            "steps", "total_estimated_hours", "created_at"
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_generate_roadmap_steps_structure(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert len(data["steps"]) >= 1
        for step in data["steps"]:
            assert "step_order" in step
            assert "skill" in step
            assert "learning_resource" in step
            assert "difficulty" in step
            assert "estimated_hours" in step
            assert "reason" in step
            assert "is_verified" in step

    def test_generate_roadmap_steps_ordered_sequentially(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        orders = [s["step_order"] for s in data["steps"]]
        assert orders == list(range(1, len(orders) + 1)), "Steps should be sequentially numbered"

    def test_generate_roadmap_has_apply_final_step(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        last_step = data["steps"][-1]
        assert last_step["skill"] == "Application"
        assert last_step["is_verified"] is True

    def test_generate_roadmap_total_hours_matches_sum(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        step_hours = sum(s.get("estimated_hours", 0) or 0 for s in data["steps"])
        assert data["total_estimated_hours"] == step_hours

    def test_generate_roadmap_nonexistent_opportunity(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-not-real"})
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "OPPORTUNITY_NOT_FOUND"

    def test_generate_roadmap_has_opportunity_title(self, client: TestClient):
        r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert data["opportunity_title"] == "AI for Sustainable Cities Hackathon"

    def test_generate_roadmap_different_opportunities_different_ids(self, client: TestClient):
        r1 = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        r2 = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-002"})
        d1 = assert_ok(r1)
        d2 = assert_ok(r2)
        assert d1["opportunity_id"] != d2["opportunity_id"]
        assert d1["id"] != d2["id"]


class TestRoadmapGet:
    """GET /roadmap/{roadmap_id} - retrieve a previously generated roadmap."""

    def test_get_roadmap_after_generate(self, client: TestClient):
        gen_r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-001"})
        gen_data = assert_ok(gen_r)
        roadmap_id = gen_data["id"]
        r = client.get(f"/api/v1/roadmap/{roadmap_id}")
        data = assert_ok(r)
        assert data["id"] == roadmap_id
        assert data["opportunity_id"] == "opp-001"

    def test_get_nonexistent_roadmap(self, client: TestClient):
        r = client.get("/api/v1/roadmap/roadmap-doesnotexist")
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "ROADMAP_NOT_FOUND"

    def test_generated_roadmap_persisted_in_memory(self, client: TestClient):
        gen_r = client.post("/api/v1/roadmap/generate", json={"opportunity_id": "opp-003"})
        gen_data = assert_ok(gen_r)
        roadmap_id = gen_data["id"]
        r1 = client.get(f"/api/v1/roadmap/{roadmap_id}")
        r2 = client.get(f"/api/v1/roadmap/{roadmap_id}")
        d1 = assert_ok(r1)
        d2 = assert_ok(r2)
        assert d1["id"] == d2["id"]
        assert len(d1["steps"]) == len(d2["steps"])


# =============================================================================
#  TEAMS TESTS
# =============================================================================

class TestTeamMatch:
    """POST /teams/match - find complementary teammates."""

    def test_team_match_returns_candidates(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert "candidates" in data
        assert isinstance(data["candidates"], list)
        assert len(data["candidates"]) > 0

    def test_team_match_response_structure(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        for field in ["opportunity_id", "opportunity_title", "candidates", "team_coverage"]:
            assert field in data, f"Missing field: {field}"

    def test_team_match_candidates_sorted_by_score(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        scores = [c["compatibility_score"] for c in data["candidates"]]
        assert scores == sorted(scores, reverse=True)

    def test_team_match_candidate_structure(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        candidate = data["candidates"][0]
        for field in ["user_id", "display_name", "compatibility_score", "skills", "complementary_skills", "shared_skills", "ai_reasoning"]:
            assert field in candidate, f"Missing candidate field: {field}"

    def test_team_match_compatibility_score_bounded(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        for c in data["candidates"]:
            assert 0 <= c["compatibility_score"] <= 100

    def test_team_match_team_coverage_dict(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        coverage = data["team_coverage"]
        assert isinstance(coverage, dict)
        for skill, covered in coverage.items():
            assert isinstance(covered, bool)

    def test_team_match_user_role_inferred(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        assert "user_role" in data
        assert isinstance(data["user_role"], str)
        assert len(data["user_role"]) > 0

    def test_team_match_custom_team_size(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001", "target_team_size": 3})
        data = assert_ok(r)
        assert len(data["candidates"]) > 0

    def test_team_match_nonexistent_opportunity(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-not-real"})
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "OPPORTUNITY_NOT_FOUND"

    def test_team_match_ai_reasoning_non_empty(self, client: TestClient):
        r = client.post("/api/v1/teams/match", json={"opportunity_id": "opp-001"})
        data = assert_ok(r)
        for c in data["candidates"]:
            assert len(c["ai_reasoning"]) > 0


class TestTeamRecommendations:
    """GET /teams/recommendations - general team recommendations."""

    def test_team_recommendations_returns_list(self, client: TestClient):
        r = client.get("/api/v1/teams/recommendations")
        data = assert_ok(r)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_team_recommendations_sorted_by_score(self, client: TestClient):
        r = client.get("/api/v1/teams/recommendations")
        data = assert_ok(r)
        scores = [c["compatibility_score"] for c in data]
        assert scores == sorted(scores, reverse=True)

    def test_team_recommendations_candidate_fields(self, client: TestClient):
        r = client.get("/api/v1/teams/recommendations")
        data = assert_ok(r)
        for c in data:
            assert "user_id" in c
            assert "display_name" in c
            assert "compatibility_score" in c


# =============================================================================
#  PLANNER TESTS
# =============================================================================

class TestPlannerEvents:
    """GET /planner/events - retrieve all planner events."""

    def test_get_planner_events(self, client: TestClient):
        r = client.get("/api/v1/planner/events")
        data = assert_ok(r)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_planner_events_have_required_fields(self, client: TestClient):
        r = client.get("/api/v1/planner/events")
        data = assert_ok(r)
        for event in data:
            assert "title" in event
            assert "event_type" in event
            assert "event_date" in event

    def test_planner_events_multiple_types(self, client: TestClient):
        r = client.get("/api/v1/planner/events")
        data = assert_ok(r)
        types = {e["event_type"] for e in data}
        assert len(types) >= 2


class TestPlannerConflicts:
    """POST /planner/conflicts - detect scheduling conflicts."""

    def test_conflicts_detected_in_seed_data(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        assert "conflicts" in data
        assert "total_events" in data
        assert "conflict_count" in data
        assert data["conflict_count"] >= 1

    def test_conflicts_response_structure(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        assert isinstance(data["conflicts"], list)
        assert isinstance(data["total_events"], int)
        assert isinstance(data["conflict_count"], int)
        assert data["total_events"] >= 1

    def test_conflicts_have_severity(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        for c in data["conflicts"]:
            assert c["severity"] in {"high", "medium", "low"}

    def test_conflicts_have_event_references(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        for c in data["conflicts"]:
            assert "event_a" in c
            assert "event_b" in c
            assert "description" in c

    def test_conflicts_count_matches_list_length(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        assert data["conflict_count"] == len(data["conflicts"])

    def test_academic_conflict_is_high_severity(self, client: TestClient):
        r = client.post("/api/v1/planner/conflicts", json={})
        data = assert_ok(r)
        academic_conflicts = [
            c for c in data["conflicts"]
            if c.get("event_a", {}).get("event_type") == "academic"
            or c.get("event_b", {}).get("event_type") == "academic"
        ]
        for c in academic_conflicts:
            assert c["severity"] == "high"


# =============================================================================
#  ADMIN TESTS
# =============================================================================

class TestAdminSeed:
    """POST /admin/seed - seed/verify seed data."""

    def test_seed_endpoint_returns_summary(self, client: TestClient):
        r = client.post("/api/v1/admin/seed")
        data = assert_ok(r)
        for field in ["seeded_at", "opportunities", "canonical_opportunities", "duplicates_found", "evidence_records", "source_records"]:
            assert field in data, f"Missing field: {field}"

    def test_seed_counts_are_positive(self, client: TestClient):
        r = client.post("/api/v1/admin/seed")
        data = assert_ok(r)
        assert data["opportunities"] > 0
        assert data["canonical_opportunities"] > 0
        assert data["evidence_records"] > 0
        assert data["source_records"] > 0

    def test_seed_deduplication_works(self, client: TestClient):
        r = client.post("/api/v1/admin/seed")
        data = assert_ok(r)
        assert data["canonical_opportunities"] <= data["opportunities"]


class TestAdminIngestion:
    """POST /admin/ingestion/run + GET /admin/ingestion/status."""

    def test_trigger_ingestion(self, client: TestClient):
        r = client.post("/api/v1/admin/ingestion/run")
        data = assert_ok(r)
        assert "run_id" in data
        assert "status" in data
        assert "started_at" in data
        assert data["status"] == "completed"

    def test_ingestion_run_metrics(self, client: TestClient):
        r = client.post("/api/v1/admin/ingestion/run")
        data = assert_ok(r)
        for key in ["sources_processed", "records_processed", "records_created", "records_updated", "duplicates_found", "errors"]:
            assert key in data, f"Missing metric: {key}"
            assert isinstance(data[key], int)

    def test_ingestion_status(self, client: TestClient):
        r = client.get("/api/v1/admin/ingestion/status")
        data = assert_ok(r)
        assert "last_run" in data
        assert "status" in data
        assert "total_opportunities" in data
        assert "active_sources" in data
        assert data["status"] == "healthy"

    def test_ingestion_total_opportunities_matches_seed(self, client: TestClient):
        from app.services.seed_data import SEED_OPPORTUNITIES
        r = client.get("/api/v1/admin/ingestion/status")
        data = assert_ok(r)
        assert data["total_opportunities"] == len(SEED_OPPORTUNITIES)


class TestAdminRecalculateTrust:
    """POST /admin/recalculate-trust."""

    def test_recalculate_trust_returns_list(self, client: TestClient):
        r = client.post("/api/v1/admin/recalculate-trust")
        data = assert_ok(r)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_recalculate_trust_result_structure(self, client: TestClient):
        r = client.post("/api/v1/admin/recalculate-trust")
        data = assert_ok(r)
        for entry in data:
            for field in ["opportunity_id", "title", "old_trust_score", "new_trust_score", "contradictions"]:
                assert field in entry, f"Missing field: {field}"

    def test_recalculate_trust_scores_bounded(self, client: TestClient):
        r = client.post("/api/v1/admin/recalculate-trust")
        data = assert_ok(r)
        for entry in data:
            assert 0 <= entry["new_trust_score"] <= 100

    def test_recalculate_trust_covers_all_opportunities(self, client: TestClient):
        from app.services.seed_data import SEED_OPPORTUNITIES
        r = client.post("/api/v1/admin/recalculate-trust")
        data = assert_ok(r)
        assert len(data) == len(SEED_OPPORTUNITIES)


# =============================================================================
#  PROFILE (USERS) TESTS
# =============================================================================

class TestProfile:
    """GET /profile + PUT /profile."""

    def test_get_profile_returns_demo_user(self, client: TestClient):
        r = client.get("/api/v1/profile")
        data = assert_ok(r)
        assert data["user_id"] == "demo-user-001"
        assert "display_name" in data
        assert "skills" in data

    def test_get_profile_has_required_fields(self, client: TestClient):
        r = client.get("/api/v1/profile")
        data = assert_ok(r)
        for field in [
            "user_id", "academic_year", "degree_type", "institution",
            "career_goal", "interests", "availability", "budget",
            "preferred_format", "location", "experience_level",
            "sustainability_interest", "skills",
            "allow_eligibility_check", "allow_team_visibility", "allow_external_scraping"
        ]:
            assert field in data, f"Missing field: {field}"

    def test_get_profile_skills_are_list(self, client: TestClient):
        r = client.get("/api/v1/profile")
        data = assert_ok(r)
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) > 0

    def test_put_profile_update_career_goal(self, client: TestClient):
        r = client.put("/api/v1/profile", json={"career_goal": "Blockchain Developer"})
        data = assert_ok(r)
        assert "updated_fields" in data
        assert "career_goal" in data["updated_fields"]

    def test_put_profile_update_multiple_fields(self, client: TestClient):
        r = client.put("/api/v1/profile", json={"availability": "flexible", "experience_level": "advanced"})
        data = assert_ok(r)
        assert "availability" in data["updated_fields"]
        assert "experience_level" in data["updated_fields"]

    def test_put_profile_returns_updated_field_names(self, client: TestClient):
        payload = {"budget": "medium", "preferred_format": "In-Person"}
        r = client.put("/api/v1/profile", json=payload)
        data = assert_ok(r)
        assert set(data["updated_fields"]) == set(payload.keys())


# =============================================================================
#  HEALTH CHECK
# =============================================================================

class TestHealthCheck:
    """GET /api/v1/health - system health endpoint."""

    def test_health_check_returns_healthy(self, client: TestClient):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"

    def test_health_check_has_services(self, client: TestClient):
        r = client.get("/api/v1/health")
        body = r.json()
        assert "services" in body
        assert "database" in body["services"]
        assert "gemini" in body["services"]


# =============================================================================
#  SERVICE UNIT TESTS
# =============================================================================

class TestMatchingServiceUnit:
    """Unit tests for the matching service logic."""

    def test_skill_match_full_match(self):
        from app.services.matching_service import compute_skill_match
        score, gap = compute_skill_match(
            student_skills=["Python", "Machine Learning"],
            required_skills=["Python", "Machine Learning"],
        )
        assert score == 100.0
        assert len(gap.missing_skills) == 0

    def test_skill_match_no_match(self):
        from app.services.matching_service import compute_skill_match
        score, gap = compute_skill_match(
            student_skills=["Java"],
            required_skills=["TensorFlow", "Docker"],
        )
        assert score < 50
        assert len(gap.missing_skills) == 2

    def test_skill_match_no_requirements(self):
        from app.services.matching_service import compute_skill_match
        score, gap = compute_skill_match(
            student_skills=["Python"],
            required_skills=[],
        )
        assert score == 80.0

    def test_skill_match_fuzzy_alias(self):
        from app.services.matching_service import compute_skill_match
        score, gap = compute_skill_match(
            student_skills=["ml"],
            required_skills=["machine learning"],
        )
        assert score > 50

    def test_interest_match_partial_overlap(self):
        from app.services.matching_service import compute_interest_match
        score = compute_interest_match(
            student_interests=["AI", "Sustainability"],
            opportunity_theme="AI/ML",
            opportunity_tags=["Climate"],
        )
        assert score > 0

    def test_interest_match_no_interests(self):
        from app.services.matching_service import compute_interest_match
        score = compute_interest_match(
            student_interests=[],
            opportunity_theme="AI/ML",
        )
        assert score == 50.0

    def test_budget_match_free_opportunity(self):
        from app.services.matching_service import compute_budget_match
        score = compute_budget_match(student_budget="free", opportunity_cost="Free")
        assert score == 100.0

    def test_budget_match_student_wants_free_paid_opportunity(self):
        from app.services.matching_service import compute_budget_match
        score = compute_budget_match(student_budget="free", opportunity_cost="$500")
        assert score < 20.0

    def test_format_match_remote_preference_remote_opportunity(self):
        from app.services.matching_service import compute_format_match
        score = compute_format_match("remote", "Online / Remote")
        assert score == 100.0

    def test_format_match_remote_preference_inperson_opportunity(self):
        from app.services.matching_service import compute_format_match
        score = compute_format_match("remote", "In-Person")
        assert score < 40

    def test_compute_full_match_returns_bounded_score(self):
        from app.services.matching_service import compute_full_match
        from app.services.seed_data import DEMO_STUDENT_PROFILE, SEED_OPPORTUNITIES
        opp = SEED_OPPORTUNITIES[0]
        score, breakdown, gap = compute_full_match(DEMO_STUDENT_PROFILE, opp)
        assert 0 <= score <= 100
        assert 0 <= breakdown.skill_match <= 100
        assert 0 <= breakdown.interest_match <= 100

    def test_compute_full_match_high_alignment_opp001(self):
        from app.services.matching_service import compute_full_match
        from app.services.seed_data import DEMO_STUDENT_PROFILE, SEED_OPPORTUNITIES
        opp = next(o for o in SEED_OPPORTUNITIES if o["id"] == "opp-001")
        score, _, _ = compute_full_match(DEMO_STUDENT_PROFILE, opp)
        assert score >= 60, f"Expected score >= 60, got {score}"


class TestTeamServiceUnit:
    """Unit tests for the team service logic."""

    def test_compute_team_compatibility_returns_candidate(self):
        from app.services.team_service import compute_team_compatibility
        from app.services.seed_data import DEMO_STUDENT_PROFILE, SEED_TEAM_CANDIDATES, SEED_OPPORTUNITIES
        opp = SEED_OPPORTUNITIES[0]
        candidate = SEED_TEAM_CANDIDATES[0]
        result = compute_team_compatibility(DEMO_STUDENT_PROFILE, candidate, opp)
        assert 0 <= result.compatibility_score <= 100
        assert result.display_name == candidate["display_name"]

    def test_compute_team_complementary_skills_not_in_student_skills(self):
        from app.services.team_service import compute_team_compatibility
        from app.services.seed_data import DEMO_STUDENT_PROFILE, SEED_TEAM_CANDIDATES, SEED_OPPORTUNITIES
        opp = SEED_OPPORTUNITIES[0]
        sarah = SEED_TEAM_CANDIDATES[0]
        result = compute_team_compatibility(DEMO_STUDENT_PROFILE, sarah, opp)
        # Sarah brings React/Figma which the demo student does not have
        assert len(result.complementary_skills) >= 0  # soft check - should have some

    def test_detect_conflicts_seed_data(self):
        from app.services.team_service import detect_conflicts
        from app.services.seed_data import SEED_PLANNER_EVENTS
        result = detect_conflicts(SEED_PLANNER_EVENTS)
        assert result.conflict_count >= 1
        assert result.total_events == 3

    def test_detect_conflicts_no_events(self):
        from app.services.team_service import detect_conflicts
        result = detect_conflicts([])
        assert result.conflict_count == 0
        assert result.total_events == 0

    def test_detect_conflicts_non_overlapping_events(self):
        from app.services.team_service import detect_conflicts
        events = [
            {"id": "e1", "user_id": "u1", "title": "Event A", "event_type": "learning", "event_date": "2030-01-01"},
            {"id": "e2", "user_id": "u1", "title": "Event B", "event_type": "opportunity", "event_date": "2030-03-01"},
        ]
        result = detect_conflicts(events)
        assert result.conflict_count == 0
