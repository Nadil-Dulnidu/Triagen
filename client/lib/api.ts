/**
 * Triagen Client API Library
 * Typed HTTP client interfacing with FastAPI backend (/api/v1).
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ReviewFinding {
  id?: string;
  severity: "critical" | "warning" | "suggestion" | "info";
  category: string;
  file_path: string;
  start_line: number;
  end_line?: number | null;
  title: string;
  description: string;
  suggestion?: string | null;
  agent_name?: string | null;
}

export interface ReviewResponse {
  id: string;
  pull_request_id: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  summary?: string | null;
  risk_level?: "low" | "medium" | "high" | "critical" | string;
  triage_classification?: string | null;
  total_findings: number;
  critical_count: number;
  warning_count: number;
  suggestion_count: number;
  duration_ms?: number | null;
  created_at: string;
  updated_at?: string;
  findings?: ReviewFinding[];
  pull_request?: {
    id: string;
    number?: number;
    pr_number?: number;
    title: string;
    author?: string;
    author_github_username?: string;
    head_branch?: string;
    base_branch?: string;
    repository?: {
      id?: string;
      full_name: string;
      name: string;
    };
  };
}

export interface RepositoryConfig {
  id?: string;
  repository_id?: string;
  security_agent_enabled: boolean;
  style_agent_enabled: boolean;
  test_coverage_agent_enabled: boolean;
  auto_review_enabled: boolean;
  custom_rules?: Record<string, unknown> | null;
  ignored_paths?: string[] | null;
  review_language?: string;
}

export interface RepositoryResponse {
  id: string;
  organization_id: string;
  github_repo_id: number;
  full_name: string;
  name: string;
  default_branch: string;
  language?: string | null;
  private?: boolean;
  is_active: boolean;
  last_review_at?: string | null;
  created_at: string;
  updated_at: string;
  config?: RepositoryConfig | null;
}

export interface GitHubAvailableRepo {
  github_repo_id: number;
  full_name: string;
  name: string;
  private: boolean;
  default_branch: string;
  language?: string | null;
  is_connected: boolean;
}

export interface AnalyticsOverview {
  total_reviews: number;
  active_repositories: number;
  total_findings_caught: number;
  critical_vulnerabilities_prevented: number;
  developer_hours_saved: number;
  avg_review_latency_seconds: number;
  severity_distribution: {
    critical: number;
    warning: number;
    suggestion: number;
    info: number;
  };
  top_categories: Array<{ category: string; count: number }>;
  agent_performance: Array<{
    agent_name: string;
    model_used: string;
    total_runs: number;
    avg_latency_ms: number;
    total_tokens: number;
  }>;
}

export interface MemoryRule {
  id: string;
  tier: "org" | "repo" | "developer";
  memory_type: string;
  key: string;
  value: string;
  organization_id?: string;
  repository_id?: string;
  user_id?: string;
  last_accessed_at?: string | null;
  created_at: string;
  updated_at: string;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// ── API Methods ─────────────────────────────────────────────────────────

export const api = {
  // Analytics
  getOverview: (token?: string | null) =>
    request<AnalyticsOverview>("/api/v1/analytics/overview", { method: "GET" }, token),

  // Reviews
  getReviews: (limit = 20, offset = 0, token?: string | null) =>
    request<ReviewResponse[]>(`/api/v1/reviews?limit=${limit}&offset=${offset}`, { method: "GET" }, token),

  getReview: (id: string, token?: string | null) =>
    request<ReviewResponse>(`/api/v1/reviews/${id}`, { method: "GET" }, token),

  seedDemoData: (token?: string | null) =>
    request<{ status: string; message: string; seeded_count: number }>(
      "/api/v1/reviews/seed",
      { method: "POST" },
      token
    ),

  // Repositories
  getRepositories: (token?: string | null) =>
    request<RepositoryResponse[]>("/api/v1/repositories", { method: "GET" }, token),

  getRepoConfig: (repoId: string, token?: string | null) =>
    request<RepositoryConfig>(`/api/v1/repositories/${repoId}/config`, { method: "GET" }, token),

  updateRepoConfig: (repoId: string, config: Partial<RepositoryConfig>, token?: string | null) =>
    request<RepositoryConfig>(
      `/api/v1/repositories/${repoId}/config`,
      {
        method: "PUT",
        body: JSON.stringify(config),
      },
      token
    ),

  disconnectRepository: (repoId: string, token?: string | null) =>
    request<void>(`/api/v1/repositories/${repoId}`, { method: "DELETE" }, token),

  getGitHubAvailableRepos: (token?: string | null) =>
    request<GitHubAvailableRepo[]>("/api/v1/github/repositories", { method: "GET" }, token),

  connectGitHubRepos: (repoIds: number[], token?: string | null) =>
    request<RepositoryResponse[]>(
      "/api/v1/github/repositories/connect",
      {
        method: "POST",
        body: JSON.stringify({ repository_ids: repoIds }),
      },
      token
    ),

  // Memory
  getOrgMemories: (token?: string | null) =>
    request<MemoryRule[]>("/api/v1/memory/org", { method: "GET" }, token),

  getRepoMemories: (repoId?: string, token?: string | null) =>
    request<MemoryRule[]>(
      repoId ? `/api/v1/memory/repo?repository_id=${repoId}` : "/api/v1/memory/repo",
      { method: "GET" },
      token
    ),

  getDeveloperMemories: (userId?: string, token?: string | null) =>
    request<MemoryRule[]>(
      userId ? `/api/v1/memory/dev?user_id=${userId}` : "/api/v1/memory/dev",
      { method: "GET" },
      token
    ),

  createOrgMemory: (data: { memory_type: string; key: string; value: string }, token?: string | null) =>
    request<MemoryRule>(
      "/api/v1/memory/org",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  createRepoMemory: (
    data: { repository_id: string; memory_type: string; key: string; value: string },
    token?: string | null
  ) =>
    request<MemoryRule>(
      "/api/v1/memory/repo",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  createDeveloperMemory: (
    data: { user_id: string; memory_type: string; key: string; value: string },
    token?: string | null
  ) =>
    request<MemoryRule>(
      "/api/v1/memory/dev",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),

  deleteOrgMemory: (id: string, token?: string | null) =>
    request<void>(`/api/v1/memory/org/${id}`, { method: "DELETE" }, token),

  deleteRepoMemory: (id: string, token?: string | null) =>
    request<void>(`/api/v1/memory/repo/${id}`, { method: "DELETE" }, token),

  deleteDeveloperMemory: (id: string, token?: string | null) =>
    request<void>(`/api/v1/memory/dev/${id}`, { method: "DELETE" }, token),
};
