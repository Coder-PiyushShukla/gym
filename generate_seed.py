import json
import os
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone.utc)
NOW_ISO = NOW.isoformat()

def _future_date(days: int) -> str:
    return (NOW + timedelta(days=days)).strftime("%d %b %Y")

def _past_date(days: int) -> str:
    return (NOW - timedelta(days=days)).strftime("%d %b %Y")

# Create 30 base opportunities
base_opps = []

# 6 AI/ML
for i in range(1, 7):
    base_opps.append({
        "id": f"opp-aiml-{i}",
        "title": f"AI/ML Challenge {i}",
        "description": f"An AI/ML competition for enthusiasts. Edition {i}.",
        "organizer": f"AI Org {i}",
        "source_url": f"https://example.com/aiml-{i}",
        "source_name": "AI Portal",
        "theme": "AI/ML",
        "start_date": _future_date(30 + i),
        "end_date": _future_date(32 + i),
        "application_deadline": _future_date(20 + i),
        "format": "Online / Remote" if i % 2 == 0 else "In-Person",
        "location": None if i % 2 == 0 else "Bangalore, India",
        "is_remote": i % 2 == 0,
        "cost": "Free" if i % 2 == 0 else "₹500",
        "team_size_min": 1,
        "team_size_max": 4,
        "required_skills": ["Python", "Machine Learning"],
        "experience_level": "intermediate",
        "sustainability_tags": [],
        "trust_score": 80 + i,
        "access_score": 90,
        "status": "active"
    })

# 4 Sustainability
for i in range(1, 5):
    base_opps.append({
        "id": f"opp-sust-{i}",
        "title": f"Climate Tech Hackathon {i}",
        "description": "Build solutions for climate change.",
        "organizer": "Green Earth",
        "source_url": f"https://example.com/sust-{i}",
        "source_name": "Green Portal",
        "theme": "Sustainability / Climate Tech",
        "start_date": _future_date(40 + i),
        "end_date": _future_date(42 + i),
        "application_deadline": _future_date(30 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "team_size_min": 2,
        "team_size_max": 5,
        "required_skills": ["Web Development", "Data Analysis"],
        "experience_level": "beginner",
        "sustainability_tags": ["Climate Action", "Clean Energy"],
        "trust_score": 85,
        "access_score": 95,
        "status": "active"
    })

# 3 Data Science
for i in range(1, 4):
    base_opps.append({
        "id": f"opp-ds-{i}",
        "title": f"Data Science Bowl {i}",
        "description": "Analyze data for insights.",
        "organizer": "Data Corp",
        "source_url": f"https://example.com/ds-{i}",
        "source_name": "Data Portal",
        "theme": "Data Science",
        "start_date": _future_date(15 + i),
        "end_date": _future_date(16 + i),
        "application_deadline": _future_date(10 + i),
        "format": "Hybrid",
        "location": "Mumbai",
        "is_remote": False,
        "cost": "Free",
        "team_size_min": 1,
        "team_size_max": 3,
        "required_skills": ["Python", "Pandas", "SQL"],
        "experience_level": "intermediate",
        "sustainability_tags": [],
        "trust_score": 92,
        "access_score": 80,
        "status": "active"
    })

# 3 Web Development
for i in range(1, 4):
    base_opps.append({
        "id": f"opp-web-{i}",
        "title": f"Web Dev Challenge {i}",
        "description": "Build modern web apps.",
        "organizer": "Web Foundation",
        "source_url": f"https://example.com/web-{i}",
        "source_name": "Web Portal",
        "theme": "Web Development",
        "start_date": _future_date(25 + i),
        "end_date": _future_date(27 + i),
        "application_deadline": _future_date(15 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "team_size_min": 1,
        "team_size_max": 2,
        "required_skills": ["React", "JavaScript", "HTML/CSS"],
        "experience_level": "beginner",
        "sustainability_tags": [],
        "trust_score": 95,
        "access_score": 90,
        "status": "active"
    })

# 3 Open Source
for i in range(1, 4):
    base_opps.append({
        "id": f"opp-os-{i}",
        "title": f"Open Source Sprint {i}",
        "description": "Contribute to open source.",
        "organizer": "OS Initiative",
        "source_url": f"https://example.com/os-{i}",
        "source_name": "OS Portal",
        "theme": "Open Source",
        "start_date": _future_date(50 + i),
        "end_date": _future_date(55 + i),
        "application_deadline": _future_date(40 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "team_size_min": 1,
        "team_size_max": 1,
        "required_skills": ["Git", "Python"],
        "experience_level": "any",
        "sustainability_tags": [],
        "trust_score": 99,
        "access_score": 100,
        "status": "active"
    })

# 3 Cybersecurity
for i in range(1, 4):
    base_opps.append({
        "id": f"opp-cyber-{i}",
        "title": f"Cyber CTF {i}",
        "description": "Capture the flag.",
        "organizer": "SecGroup",
        "source_url": f"https://example.com/cyber-{i}",
        "source_name": "Sec Portal",
        "theme": "Cybersecurity",
        "start_date": _future_date(20 + i),
        "end_date": _future_date(22 + i),
        "application_deadline": _future_date(18 + i),
        "format": "In-Person",
        "location": "Delhi",
        "is_remote": False,
        "cost": "₹1000",
        "team_size_min": 3,
        "team_size_max": 4,
        "required_skills": ["Networking", "Linux"],
        "experience_level": "advanced",
        "sustainability_tags": [],
        "trust_score": 88,
        "access_score": 60,
        "status": "active"
    })

# 2 IoT/Robotics
for i in range(1, 3):
    base_opps.append({
        "id": f"opp-iot-{i}",
        "title": f"Robotics Expo {i}",
        "description": "Build robots.",
        "organizer": "RoboOrg",
        "source_url": f"https://example.com/iot-{i}",
        "source_name": "Robo Portal",
        "theme": "IoT / Robotics",
        "start_date": _future_date(60 + i),
        "end_date": _future_date(62 + i),
        "application_deadline": _future_date(50 + i),
        "format": "In-Person",
        "location": "Pune",
        "is_remote": False,
        "cost": "Free",
        "team_size_min": 2,
        "team_size_max": 5,
        "required_skills": ["C++", "Arduino"],
        "experience_level": "intermediate",
        "sustainability_tags": [],
        "trust_score": 85,
        "access_score": 70,
        "status": "active"
    })

# 2 Social Impact
for i in range(1, 3):
    base_opps.append({
        "id": f"opp-social-{i}",
        "title": f"Social Impact Hack {i}",
        "description": "Hack for good.",
        "organizer": "NGO Connect",
        "source_url": f"https://example.com/social-{i}",
        "source_name": "NGO Portal",
        "theme": "Social Impact",
        "start_date": _future_date(70 + i),
        "end_date": _future_date(72 + i),
        "application_deadline": _future_date(60 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "team_size_min": 2,
        "team_size_max": 4,
        "required_skills": ["Web Development"],
        "experience_level": "beginner",
        "sustainability_tags": ["Social Good"],
        "trust_score": 90,
        "access_score": 95,
        "status": "active"
    })

# 2 Student Innovation
for i in range(1, 3):
    base_opps.append({
        "id": f"opp-innov-{i}",
        "title": f"Student Pitch {i}",
        "description": "Pitch your startup idea.",
        "organizer": "University VC",
        "source_url": f"https://example.com/innov-{i}",
        "source_name": "Uni Portal",
        "theme": "Student Innovation",
        "start_date": _future_date(80 + i),
        "end_date": _future_date(81 + i),
        "application_deadline": _future_date(75 + i),
        "format": "Hybrid",
        "location": "Campus",
        "is_remote": False,
        "cost": "Free",
        "team_size_min": 1,
        "team_size_max": 3,
        "required_skills": ["Presentation", "Business"],
        "experience_level": "any",
        "sustainability_tags": [],
        "trust_score": 94,
        "access_score": 85,
        "status": "active"
    })

# 2 Gen Software Engineering
for i in range(1, 3):
    base_opps.append({
        "id": f"opp-se-{i}",
        "title": f"CodeSprint {i}",
        "description": "General algorithmic coding sprint.",
        "organizer": "CodePlatform",
        "source_url": f"https://example.com/se-{i}",
        "source_name": "Code Portal",
        "theme": "Software Engineering",
        "start_date": _future_date(90 + i),
        "end_date": _future_date(92 + i),
        "application_deadline": _future_date(85 + i),
        "format": "Online / Remote",
        "location": None,
        "is_remote": True,
        "cost": "Free",
        "team_size_min": 1,
        "team_size_max": 1,
        "required_skills": ["Java", "Algorithms"],
        "experience_level": "advanced",
        "sustainability_tags": [],
        "trust_score": 96,
        "access_score": 100,
        "status": "active"
    })

# Duplication Tests
duplication_fixtures = [
    # D1 Exact duplicate (Same URL)
    {**base_opps[0], "id": "test-d1-dup", "title": "AI/ML Challenge 1 (Duplicate)", "description": "Duplicate based on URL"},
    # D2 Same event, diff URL
    {**base_opps[0], "id": "test-d2-diffurl", "source_url": "https://other.com/aiml-1-diff", "title": "AI/ML Challenge 1"},
    # D3 Similar titles, diff event
    {**base_opps[0], "id": "test-d3-similar", "title": "AI/ML Challenge 1", "start_date": _future_date(100), "source_url": "https://example.com/aiml-1-other"},
]

# Date Tests
date_fixtures = [
    # T1 Future
    {**base_opps[0], "id": "test-t1-future", "application_deadline": _future_date(5)},
    # T2 Today
    {**base_opps[0], "id": "test-t2-today", "application_deadline": NOW.strftime("%d %b %Y")},
    # T3 Yesterday
    {**base_opps[0], "id": "test-t3-yesterday", "application_deadline": _past_date(1)},
    # T4 Past month
    {**base_opps[0], "id": "test-t4-past", "application_deadline": _past_date(60)},
    # T5 Missing
    {**base_opps[0], "id": "test-t5-missing", "application_deadline": None},
]

all_opps = base_opps + duplication_fixtures + date_fixtures

with open('backend/app/services/seed_data.py', 'r') as f:
    original = f.read()

# Replace SEED_OPPORTUNITIES list in seed_data.py
import re
start_idx = original.find('SEED_OPPORTUNITIES = [')
# Find the next # ── Seed Planner Events ──────────────────────────────────────
end_idx = original.find('# ── Seed Planner Events', start_idx)

new_content = original[:start_idx] + 'SEED_OPPORTUNITIES = ' + json.dumps(all_opps, indent=4) + '\n\n\n' + original[end_idx:]

with open('backend/app/services/seed_data.py', 'w') as f:
    f.write(new_content)

print(f"Generated {len(base_opps)} base opps and {len(duplication_fixtures) + len(date_fixtures)} fixtures. Saved to seed_data.py")
