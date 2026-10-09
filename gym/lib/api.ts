/**
 * DISHA Frontend API Client
 * Typed client for all backend API endpoints.
 * Base URL: http://localhost:8000 (dev) or env-configured in production.
 *
 * Usage:
 *   import { api } from '@/lib/api'
 *   const opps = await api.opportunities.list({ is_free: true, is_remote: true })
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string };
  request_id?: string;
}

export interface Opportunity {
  id: string;
  title: string;
  description?: string;
  organizer?: string;
  theme?: string;
  format?: string;
  location?: string | null;
  is_remote?: boolean;
  cost?: string;
  start_date?: string;
  end_date?: string;
  application_deadline?: string | null;
  required_skills?: string[];
  preferred_skills?: string[];
  experience_level?: string;
  team_size_min?: number | null;
  team_size_max?: number | null;
  status?: string;
  trust_score?: number;
  access_score?: number;
  sustainability_tags?: string[];
  sdg_tags?: Array<{ sdg_id: number; label: string; reason: string }>;
  source_url?: string;
  application_url?: string;
  matchScore?: number;
  trustScore?: number;
  eligibility?: string;
  matchBreakdown?: Record<string, number>;
  whyThis?: string[];
  whyNot?: string[];
}

export interface OpportunitiesListResponse {
  items: Opportunity[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface Recommendation {
  opportunity: Opportunity;
  match_score: number;
  trust_score: number;
  access_score: number;
  eligibility_status: 'eligible' | 'ineligible' | 'unknown' | 'needs_review';
  why_this: string[];
  why_not: string[];
  skill_gap: {
    matched_skills: string[];
    missing_skills: string[];
    optional_skills: string[];
    skill_gap_score: number;
  };
  match_breakdown: Record<string, number>;
}

export interface StudentProfile {
  user_id: string;
  display_name?: string;
  academic_year?: number;
  degree_type?: string;
  institution?: string;
  career_goal?: string;
  interests?: string[];
  availability?: string;
  budget?: string;
  preferred_format?: string;
  location?: string;
  experience_level?: string;
  sustainability_interest?: boolean;
  skills?: Array<{ name: string; level: string; category?: string }>;
}

export interface SavedOpportunity {
  id: string;
  opportunity_id: string;
  saved_at: string;
  application_status: string;
  personal_notes?: string;
  opportunity?: Opportunity;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message?: string;
  related_opportunity_id?: string;
  read_at?: string | null;
  created_at: string;
}

export interface RoadmapStep {
  skill: string;
  title: string;
  description?: string;
  learning_resource?: string;
  resource_url?: string;
  estimated_hours?: number;
  difficulty?: string;
  is_verified?: boolean;
}

// ─── Core fetch helper ───────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${BASE_URL}/api/v1${path}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Attach auth token if present (from localStorage or session)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('disha_auth_token');
    if (token) {
      (defaultHeaders as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers: { ...defaultHeaders, ...(options.headers || {}) },
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      return {
        success: false,
        error: {
          code: errBody?.error?.code || `HTTP_${res.status}`,
          message: errBody?.error?.message || res.statusText,
        },
      };
    }

    const body = await res.json();
    return body as ApiResponse<T>;
  } catch (err) {
    return {
      success: false,
      error: {
        code: 'NETWORK_ERROR',
        message: err instanceof Error ? err.message : 'Network error',
      },
    };
  }
}

function buildQuery(params: Record<string, unknown>): string {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      q.append(k, String(v));
    }
  });
  const s = q.toString();
  return s ? `?${s}` : '';
}

// ─── API Namespaces ──────────────────────────────────────────────────────────

export const api = {
  // ── Health ────────────────────────────────────────────────────────────────
  health: {
    get: () => apiFetch<{ status: string; services: Record<string, unknown> }>('/health'),
  },

  // ── Opportunities ─────────────────────────────────────────────────────────
  opportunities: {
    list: (params?: {
      theme?: string;
      format?: string;
      is_remote?: boolean;
      is_free?: boolean;
      experience_level?: string;
      status?: string;
      limit?: number;
      offset?: number;
    }) => apiFetch<OpportunitiesListResponse>(`/opportunities${buildQuery(params || {})}`),

    get: (id: string) => apiFetch<Opportunity>(`/opportunities/${id}`),

    search: (body: {
      query?: string;
      is_free?: boolean;
      is_remote?: boolean;
      theme?: string;
      experience_level?: string;
      limit?: number;
      offset?: number;
    }) =>
      apiFetch<OpportunitiesListResponse>('/opportunities/search', {
        method: 'POST',
        body: JSON.stringify(body),
      }),

    evidence: (id: string) =>
      apiFetch<Array<{ field: string; status: string; excerpt?: string; source?: string }>>(
        `/opportunities/${id}/evidence`
      ),

    trust: (id: string) =>
      apiFetch<{
        trust_score: number;
        breakdown: Record<string, number>;
        sources_count: number;
        contradictions: unknown[];
        last_verified_at?: string;
      }>(`/opportunities/${id}/trust`),

    sync: () =>
      apiFetch<{ message: string }>('/opportunities/sync', { method: 'POST' }),
  },

  // ── Recommendations ───────────────────────────────────────────────────────
  recommendations: {
    generate: (params?: {
      limit?: number;
      include_expired?: boolean;
      theme_filter?: string;
      format_filter?: string;
    }) =>
      apiFetch<{ items: Recommendation[]; total: number }>('/recommendations', {
        method: 'POST',
        body: JSON.stringify(params || {}),
      }),

    get: () => apiFetch<{ items: Recommendation[]; total: number }>('/recommendations'),
  },

  // ── Eligibility ───────────────────────────────────────────────────────────
  eligibility: {
    check: (oppId: string) =>
      apiFetch<{
        status: string;
        reasons: Array<{ field: string; status: string; reason: string }>;
        overall_status: string;
      }>(`/eligibility/${oppId}`, { method: 'POST', body: '{}' }),
  },

  // ── Profile ────────────────────────────────────────────────────────────────
  profile: {
    get: () => apiFetch<StudentProfile>('/profile'),

    update: (data: Partial<StudentProfile>) =>
      apiFetch<{ updated_fields: string[] }>('/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },

  // ── Saved Opportunities ────────────────────────────────────────────────────
  saved: {
    list: (params?: { application_status?: string }) =>
      apiFetch<{ items: SavedOpportunity[]; total: number }>(
        `/saved${buildQuery(params || {})}`
      ),

    save: (oppId: string) =>
      apiFetch<{ message: string; saved: SavedOpportunity }>(`/saved/${oppId}`, {
        method: 'POST',
      }),

    unsave: (oppId: string) =>
      apiFetch<{ message: string }>(`/saved/${oppId}`, { method: 'DELETE' }),

    updateStatus: (oppId: string, status: string, notes?: string) =>
      apiFetch<{ updated: SavedOpportunity }>(
        `/saved/${oppId}/status${buildQuery({ status, notes })}`,
        { method: 'PATCH' }
      ),
  },

  // ── Notifications ──────────────────────────────────────────────────────────
  notifications: {
    list: (params?: { unread_only?: boolean; limit?: number; offset?: number }) =>
      apiFetch<{
        items: Notification[];
        total: number;
        unread_count: number;
      }>(`/notifications${buildQuery(params || {})}`),

    markRead: (notifId: string) =>
      apiFetch<{ updated: Notification }>(`/notifications/${notifId}/read`, {
        method: 'PATCH',
      }),

    markAllRead: () =>
      apiFetch<{ marked_read: number }>('/notifications/read-all', { method: 'PATCH' }),

    delete: (notifId: string) =>
      apiFetch<{ message: string }>(`/notifications/${notifId}`, { method: 'DELETE' }),
  },

  // ── Roadmap ────────────────────────────────────────────────────────────────
  roadmap: {
    generate: (oppId: string) =>
      apiFetch<{
        roadmap_id: string;
        title: string;
        steps: RoadmapStep[];
        total_hours: number;
        skill_gap_score: number;
      }>('/roadmap/generate', {
        method: 'POST',
        body: JSON.stringify({ opportunity_id: oppId }),
      }),

    get: (roadmapId: string) =>
      apiFetch<{ roadmap_id: string; steps: RoadmapStep[] }>(`/roadmap/${roadmapId}`),

    list: () =>
      apiFetch<{ items: unknown[]; total: number }>('/roadmap'),
  },

  // ── Teams ──────────────────────────────────────────────────────────────────
  teams: {
    findMatches: (oppId: string) =>
      apiFetch<{ candidates: unknown[]; total: number }>(`/teams/match/${oppId}`),

    checkConflicts: (body: { events: unknown[] }) =>
      apiFetch<{ conflicts: unknown[]; conflict_count: number }>('/planner/check-conflicts', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  },

  // ── Admin ──────────────────────────────────────────────────────────────────
  admin: {
    seed: () =>
      apiFetch<{
        opportunities: number;
        canonical_opportunities: number;
        duplicates_found: number;
      }>('/admin/seed', { method: 'POST' }),

    triggerIngestion: () =>
      apiFetch<{ status: string; records_processed: number }>('/admin/ingestion/run', {
        method: 'POST',
      }),
  },
};

// ─── Auth helpers ─────────────────────────────────────────────────────────────

export const authHelpers = {
  setToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('disha_auth_token', token);
    }
  },
  clearToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('disha_auth_token');
    }
  },
  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('disha_auth_token');
    }
    return null;
  },
};

export default api;
