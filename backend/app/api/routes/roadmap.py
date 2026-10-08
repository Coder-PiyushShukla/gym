"""
DISHA Roadmap API Routes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.dependencies import get_demo_user
from app.schemas.common import ApiResponse
from app.schemas.roadmap import RoadmapGenerateRequest, RoadmapResponse, RoadmapStep
from app.services.matching_service import compute_skill_match
from app.services.seed_data import SEED_OPPORTUNITIES
from app.core.logging import get_logger, generate_request_id

logger = get_logger("api.roadmap")

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

# In-memory roadmap store
_roadmaps: dict[str, RoadmapResponse] = {}

# Learning resource suggestions (verified/real resources)
LEARNING_RESOURCES = {
    "docker": {
        "skill": "Docker",
        "learning_resource": "Docker Getting Started Guide",
        "resource_url": "https://docs.docker.com/get-started/",
        "difficulty": "beginner",
        "estimated_hours": 8,
        "is_verified": True,
    },
    "kubernetes": {
        "skill": "Kubernetes",
        "learning_resource": "Kubernetes Basics Tutorial",
        "resource_url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "difficulty": "intermediate",
        "estimated_hours": 15,
        "is_verified": True,
    },
    "fastapi": {
        "skill": "FastAPI",
        "learning_resource": "FastAPI Official Tutorial",
        "resource_url": "https://fastapi.tiangolo.com/tutorial/",
        "difficulty": "beginner",
        "estimated_hours": 10,
        "is_verified": True,
    },
    "tensorflow": {
        "skill": "TensorFlow",
        "learning_resource": "TensorFlow Beginner Quickstart",
        "resource_url": "https://www.tensorflow.org/tutorials/quickstart/beginner",
        "difficulty": "intermediate",
        "estimated_hours": 12,
        "is_verified": True,
    },
    "deployment": {
        "skill": "Model Deployment",
        "learning_resource": "ML Model Deployment with Flask/FastAPI",
        "resource_url": "https://fastapi.tiangolo.com/tutorial/",
        "difficulty": "intermediate",
        "estimated_hours": 12,
        "is_verified": True,
    },
    "data visualization": {
        "skill": "Data Visualization",
        "learning_resource": "Matplotlib Official Tutorials",
        "resource_url": "https://matplotlib.org/stable/tutorials/index.html",
        "difficulty": "beginner",
        "estimated_hours": 6,
        "is_verified": True,
    },
    "react": {
        "skill": "React",
        "learning_resource": "React Official Tutorial",
        "resource_url": "https://react.dev/learn",
        "difficulty": "beginner",
        "estimated_hours": 15,
        "is_verified": True,
    },
    "python": {
        "skill": "Python",
        "learning_resource": "Python Official Tutorial",
        "resource_url": "https://docs.python.org/3/tutorial/",
        "difficulty": "beginner",
        "estimated_hours": 20,
        "is_verified": True,
    },
    "git": {
        "skill": "Git",
        "learning_resource": "Git Official Documentation",
        "resource_url": "https://git-scm.com/doc",
        "difficulty": "beginner",
        "estimated_hours": 5,
        "is_verified": True,
    },
    "ci/cd": {
        "skill": "CI/CD",
        "learning_resource": "GitHub Actions Quickstart",
        "resource_url": "https://docs.github.com/en/actions/quickstart",
        "difficulty": "intermediate",
        "estimated_hours": 8,
        "is_verified": True,
    },
    "machine learning": {
        "skill": "Machine Learning",
        "learning_resource": "Google ML Crash Course",
        "resource_url": "https://developers.google.com/machine-learning/crash-course",
        "difficulty": "intermediate",
        "estimated_hours": 15,
        "is_verified": True,
    },
    "sql": {
        "skill": "SQL",
        "learning_resource": "SQLBolt Interactive Tutorial",
        "resource_url": "https://sqlbolt.com/",
        "difficulty": "beginner",
        "estimated_hours": 8,
        "is_verified": True,
    },
}


@router.post("/generate", response_model=ApiResponse)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    user: dict = Depends(get_demo_user),
):
    """
    Generate a readiness roadmap for a target opportunity.
    Compares student skills vs. opportunity requirements and builds a learning path.
    """
    rid = generate_request_id()

    opp = next((o for o in SEED_OPPORTUNITIES if o.get("id") == request.opportunity_id), None)
    if not opp:
        return ApiResponse.fail("OPPORTUNITY_NOT_FOUND", "Opportunity not found", rid, 404)

    # Compute skill gap
    student_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in user.get("skills", [])
    ]

    _, skill_gap = compute_skill_match(
        student_skills=student_skills,
        required_skills=opp.get("required_skills", []),
        preferred_skills=opp.get("preferred_skills", []),
    )

    # Build roadmap steps
    steps = []
    step_order = 1

    for missing_skill in skill_gap.missing_skills + skill_gap.optional_skills:
        resource_key = missing_skill.lower().strip()
        resource = LEARNING_RESOURCES.get(resource_key)

        if resource:
            steps.append(RoadmapStep(
                step_order=step_order,
                skill=resource["skill"],
                learning_resource=resource["learning_resource"],
                resource_url=resource["resource_url"],
                difficulty=resource["difficulty"],
                estimated_hours=resource["estimated_hours"],
                reason=f"Required for {opp.get('title', 'this opportunity')}",
                is_verified=resource["is_verified"],
            ))
        else:
            # Suggest but mark as unverified
            steps.append(RoadmapStep(
                step_order=step_order,
                skill=missing_skill,
                learning_resource=f"Search for {missing_skill} tutorials",
                resource_url=None,
                difficulty="intermediate",
                estimated_hours=10,
                reason=f"Listed as requirement for {opp.get('title', 'this opportunity')}",
                is_verified=False,
            ))

        step_order += 1

    # Add a final "apply" step
    steps.append(RoadmapStep(
        step_order=step_order,
        skill="Application",
        learning_resource="Build a mini-project combining learned skills",
        resource_url=opp.get("application_url"),
        difficulty="intermediate",
        estimated_hours=8,
        reason="Apply skills in a practice project, then submit your application",
        is_verified=True,
    ))

    total_hours = sum(s.estimated_hours or 0 for s in steps)

    roadmap_id = f"roadmap-{uuid.uuid4().hex[:8]}"
    roadmap = RoadmapResponse(
        id=roadmap_id,
        opportunity_id=opp.get("id", ""),
        opportunity_title=opp.get("title", ""),
        user_id=user.get("user_id"),
        target_skills=opp.get("required_skills", []) + opp.get("preferred_skills", []),
        current_skills=[s for s in student_skills],
        gap_skills=skill_gap.missing_skills,
        steps=steps,
        total_estimated_hours=total_hours,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    # Store for retrieval
    _roadmaps[roadmap_id] = roadmap

    logger.info(
        "roadmap_generated",
        request_id=rid,
        opportunity_id=request.opportunity_id,
        gap_skills=len(skill_gap.missing_skills),
        steps=len(steps),
    )

    return ApiResponse.ok(data=roadmap.model_dump(), request_id=rid)


@router.get("/{roadmap_id}", response_model=ApiResponse)
async def get_roadmap(roadmap_id: str):
    """Get a previously generated roadmap."""
    rid = generate_request_id()

    roadmap = _roadmaps.get(roadmap_id)
    if not roadmap:
        return ApiResponse.fail("ROADMAP_NOT_FOUND", "Roadmap not found", rid, 404)

    return ApiResponse.ok(data=roadmap.model_dump(), request_id=rid)
