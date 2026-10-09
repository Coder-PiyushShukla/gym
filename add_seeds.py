import json
import copy
from datetime import datetime, timezone, timedelta

# Import the existing variables from seed_data.py without modifying the actual file yet.
# Actually it's easier to just append a giant string to seed_data.py since python code can just have list extensions.

addition = """

# --- NEW BASE OPPORTUNITIES (Making exactly 30 base) ---
# Currently there are 15 in SEED_OPPORTUNITIES. Let's add 15 more base ones.
# 6 AI/ML, 4 Sust, 3 DS, 3 Web, 3 OS, 3 Cyber, 2 IoT, 2 Social, 2 Innov, 2 SE -> total 30.
# The original 15 already cover some of these. 
# Original: AI/ML (3), Web (2), OS (1), Cyber (1), Sust (2), DS (1), IoT (1), Social (1), Innov (1), SE (2) etc.
# We will just add 15 varied ones.

# Note: We distinguish base items from test fixtures. We will just append them.

EXTRA_BASE_OPPORTUNITIES = [
    {
        "id": f"opp-base-{i}",
        "title": f"New Base Opportunity {i}",
        "description": "A fully valid base opportunity.",
        "organizer": "Demo Org",
        "source_url": f"https://example.com/base-{i}",
        "source_name": "Demo Source",
        "theme": "Software Engineering",
        "start_date": _future_date(20 + i),
        "end_date": _future_date(22 + i),
        "application_deadline": _future_date(10 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "currency": None,
        "team_size_min": 1,
        "team_size_max": 4,
        "eligibility_text": "Open to all",
        "eligibility_structured": None,
        "required_skills": ["Python"],
        "preferred_skills": [],
        "experience_level": "intermediate",
        "sustainability_tags": [],
        "sdg_tags": [],
        "application_url": f"https://example.com/apply-{i}",
        "status": "active",
        "trust_score": 90,
        "access_score": 90,
        "last_verified_at": NOW_ISO,
        "sources_count": 1,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
        "metadata": {"is_synthetic": True, "note": "DEMO DATA"},
    } for i in range(16, 31)
]


# --- DEDUPLICATION TEST FIXTURES ---
TEST_DEDUPLICATION_FIXTURES = [
    {
        # TEST D1 - Exact duplicate (Same URL)
        **SEED_OPPORTUNITIES[0],
        "id": "test-d1-exact-dup",
        "title": SEED_OPPORTUNITIES[0]["title"] + " (D1 Copy)",
        "metadata": {"is_synthetic": True, "fixture": "D1"}
    },
    {
        # TEST D2 - Same event, different URLs
        **SEED_OPPORTUNITIES[0],
        "id": "test-d2-diff-url",
        "source_url": "https://climatetechhack.org/other-page",
        "metadata": {"is_synthetic": True, "fixture": "D2"}
    },
    {
        # TEST D3 - Similar titles, different events
        **SEED_OPPORTUNITIES[0],
        "id": "test-d3-similar-title",
        "organizer": "Different Org",
        "start_date": _future_date(100),
        "metadata": {"is_synthetic": True, "fixture": "D3"}
    },
    {
        # TEST D4 - Same organizer, recurring event
        **SEED_OPPORTUNITIES[0],
        "id": "test-d4-recurring",
        "start_date": _future_date(365),
        "end_date": _future_date(367),
        "application_deadline": _future_date(350),
        "metadata": {"is_synthetic": True, "fixture": "D4"}
    },
    {
        # TEST D5 - Slightly different title
        **SEED_OPPORTUNITIES[0],
        "id": "test-d5-slight-diff",
        "title": "ai for sustainable cities hackathon",
        "metadata": {"is_synthetic": True, "fixture": "D5"}
    },
]

# --- DEADLINE AND DATE TEST FIXTURES ---
TEST_DATE_FIXTURES = [
    {
        # T1. Future deadline
        **SEED_OPPORTUNITIES[0],
        "id": "test-t1-future",
        "application_deadline": _future_date(10),
        "metadata": {"is_synthetic": True, "fixture": "T1"}
    },
    {
        # T2. Deadline today
        **SEED_OPPORTUNITIES[0],
        "id": "test-t2-today",
        "application_deadline": NOW.strftime("%d %b %Y"),
        "metadata": {"is_synthetic": True, "fixture": "T2"}
    },
    {
        # T3. Deadline yesterday
        **SEED_OPPORTUNITIES[0],
        "id": "test-t3-yesterday",
        "application_deadline": _past_date(1),
        "status": "expired",
        "metadata": {"is_synthetic": True, "fixture": "T3"}
    },
    {
        # T4. Deadline several months in the past
        **SEED_OPPORTUNITIES[0],
        "id": "test-t4-past-months",
        "application_deadline": _past_date(90),
        "status": "expired",
        "metadata": {"is_synthetic": True, "fixture": "T4"}
    },
    {
        # T5. Missing deadline
        **SEED_OPPORTUNITIES[0],
        "id": "test-t5-missing",
        "application_deadline": None,
        "metadata": {"is_synthetic": True, "fixture": "T5"}
    },
    {
        # T7. Start date after end date
        **SEED_OPPORTUNITIES[0],
        "id": "test-t7-invalid",
        "start_date": _future_date(20),
        "end_date": _future_date(10),
        "metadata": {"is_synthetic": True, "fixture": "T7"}
    },
]

# Append everything safely to SEED_OPPORTUNITIES
SEED_OPPORTUNITIES.extend(EXTRA_BASE_OPPORTUNITIES)
SEED_OPPORTUNITIES.extend(TEST_DEDUPLICATION_FIXTURES)
SEED_OPPORTUNITIES.extend(TEST_DATE_FIXTURES)

"""

with open("backend/app/services/seed_data.py", "a") as f:
    f.write(addition)

print("Successfully appended additional data to seed_data.py")
