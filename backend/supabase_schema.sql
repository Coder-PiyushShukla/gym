-- ============================================================
-- DISHA Supabase PostgreSQL Schema
-- Run in Supabase SQL Editor (idempotent).
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- A. PROFILES
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    full_name TEXT, email TEXT,
    academic_year SMALLINT CHECK (academic_year BETWEEN 1 AND 8),
    degree TEXT, college TEXT, location TEXT, career_goal TEXT, bio TEXT,
    experience_level TEXT CHECK (experience_level IN ('beginner','intermediate','advanced','any')),
    preferred_mode TEXT CHECK (preferred_mode IN ('online','offline','hybrid','any')),
    preferred_budget TEXT CHECK (preferred_budget IN ('free','low','any')),
    available_days TEXT[],
    sustainability_interest BOOLEAN NOT NULL DEFAULT FALSE,
    allow_eligibility_check BOOLEAN NOT NULL DEFAULT TRUE,
    allow_team_visibility BOOLEAN NOT NULL DEFAULT TRUE,
    allow_external_scraping BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- B. SKILLS
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE,
    category TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- C. PROFILE_SKILLS
CREATE TABLE IF NOT EXISTS profile_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level TEXT CHECK (proficiency_level IN ('beginner','intermediate','advanced')),
    years_of_experience SMALLINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (profile_id, skill_id)
);

-- D. INTERESTS
CREATE TABLE IF NOT EXISTS interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE
);

-- E. PROFILE_INTERESTS
CREATE TABLE IF NOT EXISTS profile_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    interest_id UUID NOT NULL REFERENCES interests(id) ON DELETE CASCADE,
    UNIQUE (profile_id, interest_id)
);

-- F. OPPORTUNITIES
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL, slug TEXT UNIQUE, description TEXT,
    organizer TEXT, category TEXT, themes TEXT[], required_skills TEXT[], optional_skills TEXT[],
    eligibility_criteria TEXT, eligibility_structured JSONB, academic_year_requirements TEXT[],
    experience_level TEXT, registration_url TEXT, official_source_url TEXT,
    application_start DATE, application_deadline DATE, event_start DATE, event_end DATE,
    mode TEXT, location TEXT,
    registration_fee NUMERIC(10,2), currency TEXT, stipend_min NUMERIC(10,2), stipend_max NUMERIC(10,2),
    team_min_size SMALLINT, team_max_size SMALLINT,
    beginner_friendly BOOLEAN DEFAULT FALSE,
    sustainability_relevance TEXT[], sdg_tags JSONB,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft','active','expired','cancelled','under_review')),
    verification_status TEXT DEFAULT 'unverified' CHECK (verification_status IN ('unverified','verified','under_review','rejected')),
    trust_score SMALLINT CHECK (trust_score BETWEEN 0 AND 100),
    access_score SMALLINT CHECK (access_score BETWEEN 0 AND 100),
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    last_verified_at TIMESTAMPTZ,
    sources_count SMALLINT DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- G. OPPORTUNITY_SOURCES
CREATE TABLE IF NOT EXISTS opportunity_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL, source_url TEXT NOT NULL, source_type TEXT,
    source_credibility SMALLINT CHECK (source_credibility BETWEEN 0 AND 100),
    last_checked_at TIMESTAMPTZ, source_published_at TIMESTAMPTZ,
    evidence_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (opportunity_id, source_url)
);

-- H. OPPORTUNITY_EVIDENCE
CREATE TABLE IF NOT EXISTS opportunity_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    source_id UUID REFERENCES opportunity_sources(id) ON DELETE SET NULL,
    field_name TEXT NOT NULL, extracted_value TEXT, evidence_excerpt TEXT, evidence_url TEXT,
    verification_status TEXT DEFAULT 'unverified',
    confidence NUMERIC(5,2) CHECK (confidence BETWEEN 0 AND 100),
    observed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- I. OPPORTUNITY_CONFLICTS
CREATE TABLE IF NOT EXISTS opportunity_conflicts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL, conflicting_values JSONB NOT NULL, source_ids UUID[],
    status TEXT NOT NULL DEFAULT 'unresolved' CHECK (status IN ('unresolved','resolved','dismissed')),
    resolution_notes TEXT, detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), resolved_at TIMESTAMPTZ
);

-- J. RECOMMENDATIONS
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    match_score NUMERIC(5,2) CHECK (match_score BETWEEN 0 AND 100),
    trust_score NUMERIC(5,2) CHECK (trust_score BETWEEN 0 AND 100),
    access_score NUMERIC(5,2) CHECK (access_score BETWEEN 0 AND 100),
    eligibility_status TEXT CHECK (eligibility_status IN ('eligible','ineligible','unknown','needs_review')),
    relevance_score NUMERIC(5,2), explanation TEXT,
    strengths JSONB DEFAULT '[]', gaps JSONB DEFAULT '[]', score_breakdown JSONB DEFAULT '{}',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (profile_id, opportunity_id)
);

-- K. SAVED_OPPORTUNITIES
CREATE TABLE IF NOT EXISTS saved_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    personal_notes TEXT,
    application_status TEXT DEFAULT 'considering' CHECK (application_status IN ('considering','applied','accepted','rejected','withdrawn')),
    UNIQUE (profile_id, opportunity_id)
);

-- L. ROADMAPS
CREATE TABLE IF NOT EXISTS roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    opportunity_id TEXT REFERENCES opportunities(id) ON DELETE SET NULL,
    title TEXT NOT NULL, objective TEXT, estimated_duration TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active','completed','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- M. ROADMAP_TASKS
CREATE TABLE IF NOT EXISTS roadmap_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    title TEXT NOT NULL, description TEXT, skill_name TEXT, resource_url TEXT,
    estimated_hours SMALLINT, sequence_number SMALLINT NOT NULL DEFAULT 1,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','in_progress','completed','skipped')),
    due_date DATE, completed_at TIMESTAMPTZ
);

-- N. TEAMS
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id TEXT REFERENCES opportunities(id) ON DELETE SET NULL,
    name TEXT NOT NULL, description TEXT,
    creator_profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    required_skills TEXT[],
    visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public','private','invite_only')),
    status TEXT DEFAULT 'forming' CHECK (status IN ('forming','full','active','completed','disbanded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- O. TEAM_MEMBERS
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected','removed')),
    joined_at TIMESTAMPTZ,
    UNIQUE (team_id, profile_id)
);

-- P. CALENDAR_EVENTS
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    opportunity_id TEXT REFERENCES opportunities(id) ON DELETE SET NULL,
    title TEXT NOT NULL, description TEXT,
    start_at TIMESTAMPTZ NOT NULL, end_at TIMESTAMPTZ,
    event_type TEXT DEFAULT 'opportunity' CHECK (event_type IN ('opportunity','academic','personal','deadline','learning')),
    source TEXT DEFAULT 'manual',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Q. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL, title TEXT NOT NULL, message TEXT,
    related_opportunity_id TEXT REFERENCES opportunities(id) ON DELETE SET NULL,
    read_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- R. USER_FEEDBACK
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    opportunity_id TEXT REFERENCES opportunities(id) ON DELETE SET NULL,
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE SET NULL,
    feedback_type TEXT NOT NULL,
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- S. SOURCE_SYNC_LOGS
CREATE TABLE IF NOT EXISTS source_sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), finished_at TIMESTAMPTZ,
    status TEXT DEFAULT 'running' CHECK (status IN ('running','completed','failed','partial')),
    items_discovered INTEGER DEFAULT 0, items_created INTEGER DEFAULT 0,
    items_updated INTEGER DEFAULT 0, items_skipped INTEGER DEFAULT 0,
    error_summary TEXT
);

-- T. AUDIT_LOGS
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT,
    safe_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opp_deadline ON opportunities(application_deadline);
CREATE INDEX IF NOT EXISTS idx_opp_themes ON opportunities USING GIN(themes);
CREATE INDEX IF NOT EXISTS idx_opp_skills ON opportunities USING GIN(required_skills);
CREATE INDEX IF NOT EXISTS idx_opp_title_trgm ON opportunities USING GIN(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_recs_profile ON recommendations(profile_id);
CREATE INDEX IF NOT EXISTS idx_saved_profile ON saved_opportunities(profile_id);
CREATE INDEX IF NOT EXISTS idx_notifs_profile ON notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_events_profile ON calendar_events(profile_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);

-- UPDATED_AT TRIGGER
CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;
