"""
DISHA Database Queries.
Named query functions that keep SQL/Supabase logic out of services.
"""

from __future__ import annotations

from typing import Any, Optional

from app.db.supabase import db, db_admin


# ── Opportunities ──────────────────────────────────────────────

def get_opportunities(
    filters: Optional[dict] = None,
    order_by: str = "-created_at",
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    return db.select(
        "opportunities",
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )


def get_opportunity_by_id(opp_id: str) -> Optional[dict]:
    return db.select_one("opportunities", opp_id)


def get_opportunity_evidence(opp_id: str) -> list[dict]:
    return db.select("opportunity_evidence", filters={"opportunity_id": opp_id})


def get_opportunity_sources(opp_id: str) -> list[dict]:
    return db.select("opportunity_sources", filters={"opportunity_id": opp_id})


def search_opportunities(query_embedding: list[float], limit: int = 20, threshold: float = 0.7) -> list[dict]:
    """Semantic search via pgvector cosine similarity (calls a DB function)."""
    result = db.rpc("match_opportunities", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": limit,
    })
    return result.data if result.data else []


def upsert_opportunity(data: dict) -> dict:
    rows = db_admin.upsert("opportunities", data)
    return rows[0] if rows else {}


def insert_evidence(data: dict | list[dict]) -> list[dict]:
    return db_admin.insert("opportunity_evidence", data)


def insert_opportunity_source(data: dict) -> list[dict]:
    return db_admin.insert("opportunity_sources", data)


# ── Users / Profiles ──────────────────────────────────────────

def get_student_profile(user_id: str) -> Optional[dict]:
    rows = db.select("student_profiles", filters={"user_id": user_id}, limit=1)
    return rows[0] if rows else None


def upsert_student_profile(data: dict) -> dict:
    rows = db.upsert("student_profiles", data)
    return rows[0] if rows else {}


def get_student_skills(user_id: str) -> list[dict]:
    return db.select("student_skills", filters={"user_id": user_id})


# ── Recommendations ───────────────────────────────────────────

def get_recommendations(user_id: str, limit: int = 10) -> list[dict]:
    return db.select(
        "recommendations",
        filters={"user_id": user_id},
        order_by="-overall_score",
        limit=limit,
    )


def insert_recommendation(data: dict) -> dict:
    rows = db_admin.insert("recommendations", data)
    return rows[0] if rows else {}


# ── Saved Opportunities ──────────────────────────────────────

def get_saved_opportunities(user_id: str) -> list[dict]:
    return db.select("saved_opportunities", filters={"user_id": user_id})


def save_opportunity(user_id: str, opp_id: str) -> dict:
    rows = db.insert("saved_opportunities", {"user_id": user_id, "opportunity_id": opp_id})
    return rows[0] if rows else {}


def unsave_opportunity(user_id: str, opp_id: str) -> bool:
    result = db.client.table("saved_opportunities").delete().eq(
        "user_id", user_id
    ).eq("opportunity_id", opp_id).execute()
    return bool(result.data)


# ── Planner ───────────────────────────────────────────────────

def get_planner_events(user_id: str) -> list[dict]:
    return db.select("planner_events", filters={"user_id": user_id}, order_by="event_date")


def insert_planner_event(data: dict) -> dict:
    rows = db.insert("planner_events", data)
    return rows[0] if rows else {}


# ── Teams ─────────────────────────────────────────────────────

def get_teams(user_id: str) -> list[dict]:
    return db.select("team_members", filters={"user_id": user_id})


# ── Roadmaps ─────────────────────────────────────────────────

def get_roadmap(roadmap_id: str) -> Optional[dict]:
    return db.select_one("roadmaps", roadmap_id)


def get_roadmap_steps(roadmap_id: str) -> list[dict]:
    return db.select("roadmap_steps", filters={"roadmap_id": roadmap_id}, order_by="step_order")


def insert_roadmap(data: dict) -> dict:
    rows = db_admin.insert("roadmaps", data)
    return rows[0] if rows else {}


def insert_roadmap_steps(data: list[dict]) -> list[dict]:
    return db_admin.insert("roadmap_steps", data)


# ── Admin / Observability ────────────────────────────────────

def insert_verification_run(data: dict) -> dict:
    rows = db_admin.insert("verification_runs", data)
    return rows[0] if rows else {}


def update_verification_run(run_id: str, data: dict) -> Optional[dict]:
    return db_admin.update("verification_runs", run_id, data)


def insert_agent_run(data: dict) -> dict:
    rows = db_admin.insert("agent_runs", data)
    return rows[0] if rows else {}


def update_agent_run(run_id: str, data: dict) -> Optional[dict]:
    return db_admin.update("agent_runs", run_id, data)


def get_latest_verification_run() -> Optional[dict]:
    rows = db_admin.select("verification_runs", order_by="-started_at", limit=1)
    return rows[0] if rows else None
