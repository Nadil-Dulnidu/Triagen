# PullSense — AI-Powered PR Review Platform: Implementation Plan

## Executive Summary

PullSense is an AI-powered GitHub Pull Request review platform that automates first-pass code reviews using a multi-agent workflow built with Google ADK. This document is the complete architectural blueprint — covering infrastructure, backend, frontend, AI agents, database, security, CI/CD, and phased delivery.

> [!IMPORTANT]
> **This plan reflects 34 design decisions made during the architecture interview.** Every decision is documented in the [Decision Log](#decision-log) at the end. No code should be written until this plan is approved.

---

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph "GitHub"
        GH_PR["Pull Request"]
        GH_APP["GitHub App"]
        GH_WH["Webhook"]
    end

    subgraph "Frontend — Cloud Run"
        NEXT["Next.js 15<br/>App Router + RSC"]
        CLERK_FE["Clerk Auth"]
    end

    subgraph "Backend — Cloud Run"
        API["FastAPI<br/>REST API + SSE"]
        CLERK_BE["Clerk JWT Verification"]
        WH_EP["Webhook Endpoint"]
    end

    subgraph "Workers — Cloud Run"
        CELERY["Celery Workers"]
        ADK["Google ADK Runner"]
    end

    subgraph "AI Agents"
        TRIAGE["Triage Agent<br/>Gemini Flash"]
        SEC["Security Agent<br/>Gemini Flash"]
        STYLE["Style Agent<br/>Gemini Flash"]
        TEST["Test Coverage Agent<br/>Gemini Flash"]
        CTX["Codebase Context Agent<br/>Gemini Flash"]
        AGG["Aggregator Agent<br/>Gemini Pro"]
    end

    subgraph "Data Layer"
        PG["Cloud SQL<br/>PostgreSQL 16"]
        REDIS["Memorystore<br/>Redis 7"]
        PINE["Pinecone<br/>Serverless"]
    end

    GH_PR --> GH_WH --> WH_EP
    WH_EP --> CELERY
    CELERY --> ADK
    ADK --> TRIAGE --> SEC & STYLE & TEST
    SEC & STYLE & TEST --> CTX
    CTX --> AGG
    AGG --> GH_APP --> GH_PR

    NEXT --> API
    API --> PG
    API --> REDIS
    CELERY --> PG
    CELERY --> REDIS
    CTX --> PINE

    CLERK_FE --> NEXT
    CLERK_BE --> API
```

### Data Flow: PR Review Lifecycle

```
1. Developer opens PR on GitHub
2. GitHub sends `pull_request.opened` webhook to PullSense
3. FastAPI webhook endpoint:
   a. Validates HMAC-SHA256 signature (<10ms)
   b. Stores raw event in `webhook_events` table (<50ms)
   c. Enqueues Celery task with event_id (<10ms)
   d. Returns 202 Accepted (<100ms total)
4. Celery worker picks up the task:
   a. Fetches PR diff + metadata from GitHub API
   b. Loads repo agent config from PostgreSQL
   c. Passes to ADK Runner
5. ADK Triage Agent:
   a. Classifies PR (size, type, risk level)
   b. Selects review agents from enabled pool
   c. Publishes progress via Redis pub/sub → SSE
6. Selected Review Agents run in parallel:
   a. Security Agent: vulnerability scanning, dependency audit
   b. Style Agent: coding conventions, naming, formatting
   c. Test Coverage Agent: missing tests, coverage gaps
7. Codebase Context Agent (RAG):
   a. Embeds changed files + related files
   b. Queries Pinecone for codebase context
   c. Enriches agent findings with repo-specific context
8. Aggregator Agent:
   a. Synthesizes all agent reports
   b. De-duplicates findings
   c. Prioritizes by severity
   d. Generates final review
9. GitHub integration posts:
   a. PR Review with inline comments on specific lines
   b. Summary comment with findings overview
10. Dashboard updates via SSE:
    a. Review status → complete
    b. Findings available for viewing
```

---

## 2. Repository Structure

```
PullSense-Web/
├── client/                          # Next.js 15 Frontend
│   ├── public/
│   ├── src/
│   │   ├── app/                     # App Router pages
│   │   │   ├── (auth)/              # Auth routes (login, signup)
│   │   │   ├── (dashboard)/         # Protected dashboard routes
│   │   │   │   ├── layout.tsx       # Dashboard shell (sidebar, header)
│   │   │   │   ├── page.tsx         # Dashboard home
│   │   │   │   ├── repositories/
│   │   │   │   ├── reviews/
│   │   │   │   ├── analytics/
│   │   │   │   ├── memory/
│   │   │   │   └── settings/
│   │   │   ├── api/                 # API route handlers (webhooks from Clerk)
│   │   │   ├── layout.tsx           # Root layout
│   │   │   └── page.tsx             # Landing page
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── dashboard/           # Dashboard-specific components
│   │   │   ├── reviews/             # Review display components
│   │   │   ├── repositories/        # Repo management components
│   │   │   ├── analytics/           # Charts, graphs
│   │   │   └── common/              # Shared components (header, sidebar)
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── lib/                     # Utilities, API client, constants
│   │   │   ├── api/                 # Auto-generated API client
│   │   │   ├── auth/                # Clerk helpers
│   │   │   └── utils/               # Shared utilities
│   │   ├── stores/                  # Zustand stores
│   │   └── types/                   # Auto-generated from OpenAPI
│   ├── .env.local                   # Local env vars (git-ignored)
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── package.json
│   ├── tailwind.config.ts           # Tailwind v4 (CSS-first, minimal config)
│   └── tsconfig.json
│
├── server/                          # FastAPI Backend
│   ├── src/
│   │   └── server/
│   │       ├── __init__.py
│   │       ├── main.py              # FastAPI app factory
│   │       ├── config.py            # Pydantic Settings
│   │       ├── dependencies.py      # FastAPI dependency injection
│   │       │
│   │       ├── domains/             # Domain-driven modules
│   │       │   ├── auth/            # Authentication & authorization
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py    # Auth API routes
│   │       │   │   ├── service.py   # Auth business logic
│   │       │   │   ├── repository.py# User/org data access
│   │       │   │   ├── models.py    # SQLAlchemy models (User, Org)
│   │       │   │   ├── schemas.py   # Pydantic request/response schemas
│   │       │   │   ├── middleware.py # JWT verification middleware
│   │       │   │   └── permissions.py# Permission checks
│   │       │   │
│   │       │   ├── webhooks/        # GitHub & Clerk webhook handling
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py    # Webhook endpoints
│   │       │   │   ├── service.py   # Event processing logic
│   │       │   │   ├── repository.py# Webhook event storage
│   │       │   │   ├── models.py    # WebhookEvent model
│   │       │   │   ├── schemas.py
│   │       │   │   ├── github.py    # GitHub signature validation
│   │       │   │   └── clerk.py     # Clerk webhook handling (Svix)
│   │       │   │
│   │       │   ├── repositories/    # Repository management
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py
│   │       │   │   ├── service.py
│   │       │   │   ├── repository.py
│   │       │   │   ├── models.py    # Repository, RepoConfig, RepoMember
│   │       │   │   └── schemas.py
│   │       │   │
│   │       │   ├── reviews/         # PR reviews
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py
│   │       │   │   ├── service.py
│   │       │   │   ├── repository.py
│   │       │   │   ├── models.py    # Review, ReviewFinding, ReviewComment
│   │       │   │   └── schemas.py
│   │       │   │
│   │       │   ├── agents/          # ADK agent orchestration
│   │       │   │   ├── __init__.py
│   │       │   │   ├── runner.py    # ADK runner & agent factory
│   │       │   │   ├── orchestrator.py # Agent workflow coordination
│   │       │   │   ├── base.py      # Base agent class
│   │       │   │   ├── triage.py    # Triage Agent
│   │       │   │   ├── security.py  # Security Agent
│   │       │   │   ├── style.py     # Style Agent
│   │       │   │   ├── test_coverage.py # Test Coverage Agent
│   │       │   │   ├── codebase_context.py # Codebase Context (RAG)
│   │       │   │   ├── aggregator.py# Aggregator Agent
│   │       │   │   ├── prompts/     # Agent system prompts (markdown files)
│   │       │   │   │   ├── triage.md
│   │       │   │   │   ├── security.md
│   │       │   │   │   ├── style.md
│   │       │   │   │   ├── test_coverage.md
│   │       │   │   │   ├── codebase_context.md
│   │       │   │   │   └── aggregator.md
│   │       │   │   └── tools/       # ADK tools (GitHub API, Pinecone)
│   │       │   │       ├── __init__.py
│   │       │   │       ├── github_tools.py
│   │       │   │       ├── pinecone_tools.py
│   │       │   │       └── memory_tools.py
│   │       │   │
│   │       │   ├── memory/          # Memory management
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py
│   │       │   │   ├── service.py
│   │       │   │   ├── repository.py
│   │       │   │   ├── models.py    # DeveloperMemory, RepoMemory, OrgMemory
│   │       │   │   └── schemas.py
│   │       │   │
│   │       │   ├── analytics/       # Analytics & usage tracking
│   │       │   │   ├── __init__.py
│   │       │   │   ├── router.py
│   │       │   │   ├── service.py
│   │       │   │   ├── repository.py
│   │       │   │   ├── models.py    # UsageEvent
│   │       │   │   └── schemas.py
│   │       │   │
│   │       │   └── github/          # GitHub App integration
│   │       │       ├── __init__.py
│   │       │       ├── client.py    # GitHub API client (httpx)
│   │       │       ├── auth.py      # JWT + installation token generation
│   │       │       ├── comments.py  # PR review comment posting
│   │       │       └── schemas.py   # GitHub API response models
│   │       │
│   │       ├── infrastructure/      # Cross-cutting concerns
│   │       │   ├── __init__.py
│   │       │   ├── database.py      # SQLAlchemy async engine + session
│   │       │   ├── redis.py         # Redis client setup
│   │       │   ├── pinecone.py      # Pinecone client setup
│   │       │   ├── celery_app.py    # Celery configuration
│   │       │   ├── sse.py           # SSE event broadcaster
│   │       │   ├── rate_limiter.py  # Redis token bucket
│   │       │   ├── circuit_breaker.py # Circuit breaker implementation
│   │       │   ├── cache.py         # Redis cache decorator
│   │       │   └── logging.py       # structlog configuration
│   │       │
│   │       └── workers/             # Celery task definitions
│   │           ├── __init__.py
│   │           ├── review_tasks.py  # Review pipeline tasks
│   │           ├── indexing_tasks.py # RAG indexing tasks
│   │           ├── sync_tasks.py    # Clerk/GitHub sync tasks
│   │           └── cleanup_tasks.py # Cleanup & maintenance
│   │
│   ├── migrations/                  # Alembic migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── .env                         # Local env vars (git-ignored)
│   ├── Dockerfile
│   ├── Dockerfile.worker            # Separate image for Celery workers
│   └── pyproject.toml
│
├── infrastructure/                  # Terraform + Docker
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── cloud_run/
│   │   │   ├── cloud_sql/
│   │   │   ├── memorystore/
│   │   │   ├── secret_manager/
│   │   │   ├── artifact_registry/
│   │   │   ├── iam/
│   │   │   └── vpc/
│   │   ├── environments/
│   │   │   ├── staging/
│   │   │   │   ├── main.tf
│   │   │   │   └── terraform.tfvars
│   │   │   └── production/
│   │   │       ├── main.tf
│   │   │       └── terraform.tfvars
│   │   └── backend.tf              # GCS remote state
│   └── docker/
│       └── docker-compose.yml       # Local development
│
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Lint, test, build on PRs
│       ├── cd-staging.yml           # Deploy to staging on merge to main
│       ├── cd-production.yml        # Deploy to production (manual trigger)
│       └── openapi-sync.yml         # Auto-generate TypeScript client
│
├── scripts/                         # Developer scripts
│   ├── setup.sh                     # Initial project setup
│   ├── generate-api-client.sh       # Generate TS client from OpenAPI
│   └── seed-db.sh                   # Seed development database
│
├── assets/                          # Design assets & docs
│   ├── diagrams.excalidraw
│   ├── docs/
│   └── images/
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 3. Database Schema (ERD)

```mermaid
erDiagram
    organizations ||--o{ users : "has members"
    organizations ||--o{ repositories : "owns"
    organizations ||--o{ org_memories : "has"
    organizations ||--o{ usage_events : "tracks"

    users ||--o{ organization_memberships : "belongs to"
    organizations ||--o{ organization_memberships : "has"

    users ||--o{ developer_memories : "has"

    repositories ||--o{ repo_members : "has members"
    users ||--o{ repo_members : "member of"
    repositories ||--o{ repo_configs : "configured with"
    repositories ||--o{ pull_requests : "has"
    repositories ||--o{ repo_memories : "has"

    pull_requests ||--o{ reviews : "reviewed by"
    reviews ||--o{ review_findings : "contains"
    reviews ||--o{ review_agent_runs : "executed by"

    webhook_events ||--o{ reviews : "triggers"

    organizations {
        uuid id PK
        string clerk_org_id UK
        string name
        string slug
        string github_installation_id
        int review_rate_limit
        jsonb settings
        timestamp created_at
        timestamp updated_at
    }

    users {
        uuid id PK
        string clerk_user_id UK
        string email
        string username
        string display_name
        string avatar_url
        string github_username
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }

    organization_memberships {
        uuid id PK
        uuid user_id FK
        uuid organization_id FK
        string role "admin | member"
        timestamp created_at
    }

    repositories {
        uuid id PK
        uuid organization_id FK
        bigint github_repo_id UK
        string full_name "owner/repo"
        string name
        string default_branch
        string language
        boolean is_active
        timestamp last_review_at
        timestamp created_at
        timestamp updated_at
    }

    repo_members {
        uuid id PK
        uuid repository_id FK
        uuid user_id FK
        string role "admin | member"
        timestamp created_at
    }

    repo_configs {
        uuid id PK
        uuid repository_id FK
        boolean security_agent_enabled
        boolean style_agent_enabled
        boolean test_coverage_agent_enabled
        boolean auto_review_enabled
        jsonb custom_rules
        jsonb ignored_paths
        string review_language "en"
        timestamp created_at
        timestamp updated_at
    }

    pull_requests {
        uuid id PK
        uuid repository_id FK
        bigint github_pr_id
        int pr_number
        string title
        string author_github_username
        string head_sha
        string base_branch
        string head_branch
        string status "open | closed | merged"
        int additions
        int deletions
        int changed_files
        timestamp github_created_at
        timestamp created_at
        timestamp updated_at
    }

    reviews {
        uuid id PK
        uuid pull_request_id FK
        uuid webhook_event_id FK
        string status "pending | triaging | reviewing | aggregating | posting | completed | failed"
        string triage_classification "small | medium | large | critical"
        jsonb triage_metadata
        text summary
        int total_findings
        int critical_count
        int warning_count
        int suggestion_count
        bigint github_review_id
        int duration_ms
        int total_tokens_used
        text error_message
        int retry_count
        timestamp started_at
        timestamp completed_at
        timestamp created_at
    }

    review_findings {
        uuid id PK
        uuid review_id FK
        string agent_name "security | style | test_coverage | codebase_context"
        string severity "critical | warning | suggestion | info"
        string category
        string file_path
        int start_line
        int end_line
        text title
        text description
        text suggestion
        text code_snippet
        jsonb metadata
        timestamp created_at
    }

    review_agent_runs {
        uuid id PK
        uuid review_id FK
        string agent_name
        string model_used
        string status "pending | running | completed | failed"
        int duration_ms
        int input_tokens
        int output_tokens
        jsonb raw_output
        text error_message
        timestamp started_at
        timestamp completed_at
    }

    webhook_events {
        uuid id PK
        uuid organization_id FK
        string event_type "pull_request | installation | etc"
        string action "opened | synchronize | etc"
        string delivery_id UK
        jsonb headers
        jsonb payload
        string processing_status "pending | processing | completed | failed"
        text error_message
        timestamp processed_at
        timestamp created_at
    }

    usage_events {
        uuid id PK
        uuid organization_id FK
        uuid repository_id FK
        uuid user_id FK
        string event_type "review_started | review_completed | agent_invocation | etc"
        jsonb metadata
        timestamp created_at
    }

    developer_memories {
        uuid id PK
        uuid user_id FK
        uuid organization_id FK
        string memory_type "preference | pattern | feedback"
        text key
        text value
        jsonb metadata
        float relevance_score
        timestamp last_accessed_at
        timestamp created_at
        timestamp updated_at
    }

    repo_memories {
        uuid id PK
        uuid repository_id FK
        string memory_type "convention | architecture | tech_debt | decision"
        text key
        text value
        jsonb metadata
        float relevance_score
        timestamp last_accessed_at
        timestamp created_at
        timestamp updated_at
    }

    org_memories {
        uuid id PK
        uuid organization_id FK
        string memory_type "standard | policy | compliance"
        text key
        text value
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
```

### Key Schema Decisions

- **UUIDs everywhere** — No auto-increment IDs. UUIDs are safe for distributed systems and don't leak sequence information.
- **`organization_id` on every tenant-scoped table** — Enforces row-level isolation. Every repository query includes `WHERE organization_id = :org_id`.
- **`webhook_events` as audit log** — Raw webhook payloads stored for debugging and replay.
- **`review_agent_runs`** — Per-agent telemetry (tokens, latency, errors) for cost tracking and debugging.
- **JSONB for flexible fields** — `metadata`, `custom_rules`, `settings` use JSONB for schema flexibility without migrations.
- **Indexes** — Create indexes on: `(organization_id)` on all tenant tables, `(github_repo_id)`, `(github_pr_id, repository_id)`, `(review_id, agent_name)`, `(created_at)` for time-range queries.

---

## 4. API Design

### 4.1 API Prefix & Versioning

All backend APIs are versioned under `/api/v1/`.

### 4.2 Endpoints

#### Authentication & Users

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/users/me` | Get current user profile | JWT |
| `PATCH` | `/api/v1/users/me` | Update user profile | JWT |
| `GET` | `/api/v1/users/me/organizations` | List user's organizations | JWT |

#### Webhooks (No Auth — signature-verified)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/v1/webhooks/github` | GitHub webhook receiver | HMAC-SHA256 |
| `POST` | `/api/v1/webhooks/clerk` | Clerk webhook receiver | Svix signature |

#### Organizations

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/organizations/:org_id` | Get organization details | JWT + member |
| `PATCH` | `/api/v1/organizations/:org_id` | Update organization settings | JWT + admin |
| `GET` | `/api/v1/organizations/:org_id/members` | List org members | JWT + member |

#### Repositories

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/organizations/:org_id/repositories` | List connected repositories | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id` | Get repository details | JWT + member |
| `PATCH` | `/api/v1/organizations/:org_id/repositories/:repo_id` | Update repo settings | JWT + repo admin |
| `DELETE` | `/api/v1/organizations/:org_id/repositories/:repo_id` | Disconnect repository | JWT + org admin |
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id/config` | Get agent configuration | JWT + member |
| `PUT` | `/api/v1/organizations/:org_id/repositories/:repo_id/config` | Update agent configuration | JWT + repo admin |

#### Pull Requests & Reviews

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id/pull-requests` | List PRs | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id/pull-requests/:pr_id` | Get PR details | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id/pull-requests/:pr_id/reviews` | List reviews for PR | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/reviews/:review_id` | Get full review with findings | JWT + member |
| `POST` | `/api/v1/organizations/:org_id/reviews/:review_id/re-review` | Trigger re-review | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/reviews/:review_id/stream` | SSE stream for review progress | JWT + member |

#### Memory

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/organizations/:org_id/memory` | List org memories | JWT + admin |
| `POST` | `/api/v1/organizations/:org_id/memory` | Create org memory | JWT + admin |
| `DELETE` | `/api/v1/organizations/:org_id/memory/:memory_id` | Delete org memory | JWT + admin |
| `GET` | `/api/v1/organizations/:org_id/repositories/:repo_id/memory` | List repo memories | JWT + repo admin |
| `GET` | `/api/v1/organizations/:org_id/developers/:user_id/memory` | List developer memories | JWT + admin |

#### Analytics

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/organizations/:org_id/analytics/overview` | Dashboard overview stats | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/analytics/reviews` | Review analytics (time range) | JWT + member |
| `GET` | `/api/v1/organizations/:org_id/analytics/agents` | Agent performance stats | JWT + admin |
| `GET` | `/api/v1/organizations/:org_id/analytics/developers` | Developer trend analytics | JWT + admin |

#### GitHub App

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/github/install-url` | Get GitHub App installation URL | JWT |
| `GET` | `/api/v1/github/repositories` | List available GitHub repos (from installation) | JWT |
| `POST` | `/api/v1/github/repositories/connect` | Connect selected repos | JWT + admin |

#### Health

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Health check (DB, Redis, Celery) | None |
| `GET` | `/ready` | Readiness check | None |

---

## 5. Authentication Flow

### 5.1 Sequence Diagram: User Login

```
User                 Next.js              Clerk              FastAPI
 │                     │                    │                   │
 │─── Click Login ────►│                    │                   │
 │                     │─── Redirect ──────►│                   │
 │                     │                    │                   │
 │─── GitHub OAuth ───►│                    │                   │
 │                     │◄── JWT Token ──────│                   │
 │                     │                    │                   │
 │                     │─── API Request ───►│                   │
 │                     │    (Bearer JWT)    │                   │
 │                     │                    │   ┌───────────────┐
 │                     │                    │   │ Verify JWT    │
 │                     │                    │   │ Extract       │
 │                     │                    │   │ clerk_user_id │
 │                     │                    │   │ + org_id      │
 │                     │                    │   │ Lookup        │
 │                     │                    │   │ internal user │
 │                     │                    │   └───────────────┘
 │                     │◄── Response ───────│                   │
 │◄── Dashboard ───────│                    │                   │
```

### 5.2 Clerk-to-PostgreSQL Sync

```
Clerk                      FastAPI Webhook          PostgreSQL
 │                              │                       │
 │── user.created ─────────────►│                       │
 │   (Svix signed)             │── INSERT user ────────►│
 │                              │                       │
 │── organization.created ─────►│                       │
 │                              │── INSERT org ─────────►│
 │                              │                       │
 │── organizationMembership    ►│                       │
 │   .created                   │── INSERT membership ──►│
 │                              │                       │
 │── user.updated ─────────────►│                       │
 │                              │── UPDATE user ────────►│
 │                              │                       │
 │── user.deleted ─────────────►│                       │
 │                              │── Soft delete user ───►│
```

### 5.3 JWT Verification Middleware

```python
# Pseudocode for auth middleware
async def verify_jwt(request: Request) -> AuthContext:
    token = extract_bearer_token(request)
    claims = verify_clerk_jwt(token, clerk_jwks)  # Local verification, no API call
    
    user = await user_repo.get_by_clerk_id(claims["sub"])
    org_id = claims.get("org_id")
    org = await org_repo.get_by_clerk_id(org_id) if org_id else None
    
    return AuthContext(user=user, organization=org, role=claims.get("org_role"))
```

---

## 6. GitHub Integration Flow

### 6.1 GitHub App Setup

```
Required Permissions:
  Repository:
    - Pull requests: Read & Write (read PRs, post reviews)
    - Contents: Read (read file contents for RAG)
    - Metadata: Read (repo info)
    - Checks: Read & Write (future: Check Runs)
  Organization:
    - Members: Read (org membership info)

Webhook Events:
    - pull_request (opened, synchronize, reopened)
    - installation (created, deleted)
    - installation_repositories (added, removed)
```

### 6.2 Installation Flow

```
User                 PullSense Dashboard       GitHub              FastAPI
 │                        │                      │                    │
 │── "Connect GitHub" ───►│                      │                    │
 │                        │── GET install-url ───►│                    │
 │                        │◄── URL ──────────────│                    │
 │── Redirect ───────────►│                      │                    │
 │                        │                      │                    │
 │                    (User selects repos on GitHub)                  │
 │                        │                      │                    │
 │                        │    installation      │                    │
 │                        │    webhook ──────────►│── Process: ───────│
 │                        │                      │   1. Validate sig  │
 │                        │                      │   2. Store event   │
 │                        │                      │   3. Create/update │
 │                        │                      │      installation  │
 │                        │                      │   4. Sync repos    │
 │                        │                      │                    │
 │◄── Redirect back ──────│                      │                    │
 │                        │── Fetch repos ───────│                    │
 │◄── Show connected repos│                      │                    │
```

### 6.3 PR Review Posting

```python
# Pseudocode for posting review to GitHub
async def post_review(review: Review, findings: list[Finding]):
    token = await generate_installation_token(installation_id)

    comments = []
    for finding in findings:
        if finding.file_path and finding.start_line:
            comments.append(
                {
                    "path": finding.file_path,
                    "line": finding.start_line,
                    "body": format_inline_comment(finding),  # 🔴/🟡/🟢 + description
                }
            )

    # POST /repos/{owner}/{repo}/pulls/{pr_number}/reviews
    await github_client.create_review(
        owner=repo.owner,
        repo=repo.name,
        pr_number=pr.pr_number,
        event="COMMENT",  # Never APPROVE or REQUEST_CHANGES
        body=format_review_summary(review),
        comments=comments,
    )
```

---

## 7. ADK Agent Architecture

### 7.1 Agent Workflow (Sequence)

```
Celery Worker           ADK Runner          Agents                    External
    │                      │                   │                         │
    │── start_review ─────►│                   │                         │
    │                      │                   │                         │
    │                      │── run(triage) ───►│                         │
    │                      │                   │── classify PR ─────────►│ (analyze diff)
    │                      │                   │◄── {size, risk, ────────│
    │                      │                   │     agents_to_run}      │
    │                      │◄─ triage_result ──│                         │
    │                      │                   │                         │
    │                      │ ┌─ PARALLEL ──────────────────────────────┐ │
    │                      │ │ run(security) ──►│── analyze security ──►│ │
    │                      │ │ run(style) ─────►│── analyze style ─────►│ │
    │                      │ │ run(test_cov) ──►│── analyze tests ─────►│ │
    │                      │ └─────────────────────────────────────────┘ │
    │                      │                   │                         │
    │                      │── run(context) ──►│                         │
    │                      │                   │── embed files ─────────►│ Pinecone
    │                      │                   │── query context ───────►│ Pinecone
    │                      │                   │◄── relevant context ────│
    │                      │◄─ context_result ─│                         │
    │                      │                   │                         │
    │                      │── run(aggregator) ►│                         │
    │                      │                   │── synthesize all ──────►│ Gemini Pro
    │                      │                   │◄── final review ────────│
    │                      │◄─ final_review ───│                         │
    │                      │                   │                         │
    │◄── review_complete ──│                   │                         │
```

### 7.2 Agent Configuration (Per Agent)

```python
# Each agent is configured independently
AGENT_CONFIGS = {
    "triage": {
        "model": "gemini-2.5-flash",
        "temperature": 0.1,  # Low for classification
        "max_output_tokens": 1024,
        "system_prompt": "prompts/triage.md",
        "tools": [],  # No tools needed
    },
    "security": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2,
        "max_output_tokens": 4096,
        "system_prompt": "prompts/security.md",
        "tools": ["get_file_content", "search_dependencies"],
    },
    "style": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2,
        "max_output_tokens": 4096,
        "system_prompt": "prompts/style.md",
        "tools": ["get_file_content"],
    },
    "test_coverage": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2,
        "max_output_tokens": 4096,
        "system_prompt": "prompts/test_coverage.md",
        "tools": ["get_file_content", "list_test_files"],
    },
    "codebase_context": {
        "model": "gemini-2.5-flash",
        "temperature": 0.1,
        "max_output_tokens": 4096,
        "system_prompt": "prompts/codebase_context.md",
        "tools": ["embed_files", "query_pinecone", "get_repo_memory"],
    },
    "aggregator": {
        "model": "gemini-2.5-pro",  # Pro for synthesis quality
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "system_prompt": "prompts/aggregator.md",
        "tools": ["get_developer_memory", "get_org_memory"],
    },
}
```

### 7.3 Adding New Agents

New agents follow a simple pattern:

1. Create `server/domains/agents/new_agent.py` implementing the base agent interface
2. Create `server/domains/agents/prompts/new_agent.md` with the system prompt
3. Add configuration to `AGENT_CONFIGS`
4. Register in the agent factory
5. Add to repo config options (enable/disable)

No other changes needed — the orchestrator discovers agents dynamically.

---

## 8. RAG Architecture

### 8.1 On-Demand Indexing Flow

```
PR Opened                                    Pinecone
    │                                           │
    │── Celery task: index_pr_context           │
    │                                           │
    │── 1. Fetch changed files from GitHub      │
    │── 2. Identify related files:              │
    │       - Import targets                    │
    │       - Same directory siblings           │
    │       - Corresponding test files          │
    │       - Package configs (pyproject, etc)   │
    │── 3. Chunk files (by function/class)       │
    │── 4. Embed chunks via Gemini embedding    │
    │── 5. Upsert to Pinecone ────────────────►│
    │       namespace: "{org_id}/{repo_id}"     │
    │       metadata: {                         │
    │         pr_id, file_path,                 │
    │         chunk_type, language              │
    │       }                                   │
    │                                           │
    │── 6. Agent queries during review:         │
    │       "How does auth work in this repo?"  │
    │       → Semantic search in namespace ────►│
    │       ← Top-K relevant chunks ◄───────────│
    │                                           │
    │── 7. Cleanup after review (optional):     │
    │       Delete PR-scoped vectors ──────────►│
```

### 8.2 Pinecone Index Structure

```
Index: "pullsense"

Namespaces:
  - "{org_id}/{repo_id}"          # Codebase context per repo
  - "conventions/{org_id}"         # Team conventions (manually managed)
  - "security-knowledge"           # Shared security knowledge base

Vector Metadata:
  - org_id: string
  - repo_id: string
  - pr_id: string (nullable)
  - file_path: string
  - chunk_type: "function" | "class" | "module" | "config"
  - language: string
  - last_updated: timestamp

Embedding:
  - Model: text-embedding-004
  - Dimensions: 768
```

---

## 9. Memory Architecture

### 9.1 Memory Types & Storage

| Memory Type | Storage | Access Pattern | Example |
|---|---|---|---|
| **Temporary** | Redis (hash, 1hr TTL) | Key-value per review session | Agent intermediate outputs, triage result |
| **Developer** | PostgreSQL `developer_memories` | Query by user_id + org_id | "Prefers functional style", "Ignores var naming for scripts" |
| **Repository** | PostgreSQL `repo_memories` | Query by repo_id | "Uses hexagonal architecture", "Auth is in /src/auth/" |
| **Organization** | PostgreSQL `org_memories` | Query by org_id | "All APIs must have OpenAPI docs", "No console.log in production" |

### 9.2 Memory Learning

Memories are populated through:
1. **Explicit**: Admin creates org/repo memories via dashboard
2. **Implicit (future)**: Aggregator Agent detects patterns over multiple reviews and suggests memories
3. **Feedback loop (future)**: When a developer dismisses a finding repeatedly, create a developer memory to stop suggesting it

---

## 10. Background Workers (Celery)

### 10.1 Task Architecture

```python
# Task routing with priority queues
CELERY_TASK_ROUTES = {
    "workers.review_tasks.process_review": {"queue": "reviews"},
    "workers.review_tasks.re_review": {"queue": "reviews-priority"},
    "workers.indexing_tasks.index_pr_context": {"queue": "indexing"},
    "workers.sync_tasks.sync_installation": {"queue": "sync"},
    "workers.cleanup_tasks.cleanup_vectors": {"queue": "cleanup"},
}


# Review pipeline as Celery chain
def trigger_review(webhook_event_id: str):
    pipeline = chain(
        validate_and_prepare.s(webhook_event_id),
        run_triage.s(),
        run_parallel_agents.s(),  # Uses group() internally
        run_codebase_context.s(),
        run_aggregator.s(),
        post_github_review.s(),
        update_review_status.s(),
    )
    pipeline.apply_async()
```

### 10.2 Retry Configuration

```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,        # Base delay
    retry_backoff=True,            # Exponential backoff
    retry_backoff_max=300,         # Max 5 min between retries
    retry_jitter=True,             # Random jitter
    acks_late=True,                # Re-deliver if worker crashes
    reject_on_worker_lost=True,
)
def process_review(self, webhook_event_id: str):
    try:
        # ... review logic
    except GitHubRateLimitError as e:
        raise self.retry(countdown=e.retry_after)
    except TransientError as e:
        raise self.retry(exc=e)
    except PermanentError as e:
        # Don't retry, send to DLQ
        send_to_dlq(webhook_event_id, error=str(e))
        raise
```

---

## 11. Real-Time Updates (SSE)

### 11.1 Architecture

```
Celery Worker         Redis Pub/Sub        FastAPI SSE          Next.js Client
     │                     │                    │                     │
     │── publish ─────────►│                    │                     │
     │   channel:          │── message ────────►│                     │
     │   review:{id}       │                    │── SSE event ───────►│
     │   data: {           │                    │   data: {           │
     │     status,         │                    │     status,         │
     │     agent,          │                    │     agent,          │
     │     progress        │                    │     progress        │
     │   }                 │                    │   }                 │
```

### 11.2 Event Types

```typescript
type SSEEvent =
  | { type: "review.started"; data: { review_id: string } }
  | { type: "review.triage_complete"; data: { classification: string; agents: string[] } }
  | { type: "agent.started"; data: { agent: string } }
  | { type: "agent.completed"; data: { agent: string; findings_count: number } }
  | { type: "review.aggregating"; data: {} }
  | { type: "review.posting"; data: {} }
  | { type: "review.completed"; data: { review_id: string; total_findings: number } }
  | { type: "review.failed"; data: { error: string } };
```

---

## 12. Infrastructure (GCP + Terraform)

### 12.1 Architecture Diagram

```mermaid
graph TB
    subgraph "Google Cloud Platform"
        subgraph "Cloud Run"
            API_SVC["API Service<br/>FastAPI<br/>min: 0, max: 10"]
            WORKER_SVC["Worker Service<br/>Celery<br/>min: 1, max: 5"]
            CLIENT_SVC["Client Service<br/>Next.js<br/>min: 0, max: 5"]
        end

        subgraph "Data"
            CSQL["Cloud SQL<br/>PostgreSQL 16<br/>db-f1-micro (start)"]
            REDIS_MS["Memorystore<br/>Redis 7<br/>1GB (start)"]
        end

        subgraph "Networking"
            VPC["VPC Connector"]
            LB["Cloud Load Balancer"]
        end

        subgraph "Security"
            SM["Secret Manager"]
            IAM["IAM Roles"]
        end

        subgraph "CI/CD"
            AR["Artifact Registry<br/>Docker images"]
        end
    end

    LB --> API_SVC & CLIENT_SVC
    API_SVC --> VPC --> CSQL & REDIS_MS
    WORKER_SVC --> VPC
    CLIENT_SVC --> API_SVC

    SM --> API_SVC & WORKER_SVC & CLIENT_SVC
```

### 12.2 Terraform Module Structure

```hcl
# infrastructure/terraform/main.tf
module "vpc" {
  source = "./modules/vpc"
}

module "cloud_sql" {
  source     = "./modules/cloud_sql"
  vpc_id     = module.vpc.id
  tier       = "db-f1-micro"  # Upgrade as needed
  db_version = "POSTGRES_16"
}

module "memorystore" {
  source  = "./modules/memorystore"
  vpc_id  = module.vpc.id
  tier    = "BASIC"
  size_gb = 1
}

module "secret_manager" {
  source  = "./modules/secret_manager"
  secrets = var.secrets
}

module "artifact_registry" {
  source = "./modules/artifact_registry"
}

module "cloud_run_api" {
  source    = "./modules/cloud_run"
  name      = "pullsense-api"
  image     = "${module.artifact_registry.url}/api:latest"
  vpc       = module.vpc.connector_id
  secrets   = module.secret_manager.secret_refs
  min_instances = 0
  max_instances = 10
}

module "cloud_run_worker" {
  source    = "./modules/cloud_run"
  name      = "pullsense-worker"
  image     = "${module.artifact_registry.url}/worker:latest"
  vpc       = module.vpc.connector_id
  secrets   = module.secret_manager.secret_refs
  min_instances = 1  # Always running for webhook processing
  max_instances = 5
  no_traffic = true  # Not publicly accessible
}

module "cloud_run_client" {
  source    = "./modules/cloud_run"
  name      = "pullsense-client"
  image     = "${module.artifact_registry.url}/client:latest"
  min_instances = 0
  max_instances = 5
}
```

---

## 13. Configuration (Environment Variables)

### 13.1 Backend (.env)

```bash
# Application
APP_ENV=development                   # development | staging | production
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
APP_CORS_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pullsense

# Redis
REDIS_URL=redis://localhost:6379/0

# Clerk
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json

# GitHub App
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=./github-app.pem
GITHUB_WEBHOOK_SECRET=whsec_...
GITHUB_APP_CLIENT_ID=Iv1.abc123
GITHUB_APP_CLIENT_SECRET=secret_...

# Google AI
GOOGLE_AI_API_KEY=AIza...
GEMINI_FLASH_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-004

# Pinecone
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=pullsense
PINECONE_ENVIRONMENT=us-east-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Rate Limiting
RATE_LIMIT_REVIEWS_PER_HOUR=100
```

### 13.2 Frontend (.env.local)

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_API_URL=http://localhost:8000

CLERK_SECRET_KEY=sk_test_...
```

### 13.3 Pydantic Settings (Type-Safe Validation)

```python
# server/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = False
    app_log_level: str = "INFO"
    app_cors_origins: list[str] = ["http://localhost:3000"]

    # Database
    database_url: str

    # Redis
    redis_url: str

    # Clerk
    clerk_secret_key: str
    clerk_webhook_secret: str
    clerk_jwks_url: str

    # GitHub
    github_app_id: int
    github_app_private_key_path: str
    github_webhook_secret: str

    # Google AI
    google_ai_api_key: str
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    embedding_model: str = "text-embedding-004"

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "pullsense"

    # Celery
    celery_broker_url: str
    celery_result_backend: str

    # Rate Limiting
    rate_limit_reviews_per_hour: int = 100

    model_config = {"env_file": ".env", "case_sensitive": False}
```

---

## 14. Observability

### 14.1 Structured Logging (structlog)

```python
# Every log entry is structured JSON
logger.info(
    "review_started",
    review_id=review.id,
    repository=repo.full_name,
    pr_number=pr.pr_number,
    triage_classification=triage.classification,
    agents_selected=triage.agents,
    organization_id=str(org.id),
)
```

### 14.2 Key Metrics to Track

| Metric | Type | Description |
|---|---|---|
| `review_duration_seconds` | Histogram | Total review pipeline latency |
| `agent_duration_seconds` | Histogram | Per-agent execution time (labeled by agent) |
| `review_findings_total` | Counter | Total findings (labeled by severity) |
| `agent_tokens_total` | Counter | LLM tokens used (labeled by agent, model) |
| `webhook_processing_seconds` | Histogram | Webhook-to-ACK latency |
| `github_api_errors_total` | Counter | GitHub API errors (labeled by status code) |
| `celery_task_failures_total` | Counter | Failed Celery tasks (labeled by task name) |
| `active_reviews` | Gauge | Currently processing reviews |

### 14.3 Alerting Rules

| Alert | Condition | Severity |
|---|---|---|
| High review failure rate | >10% reviews failing in 15 min | Critical |
| Review latency spike | P95 > 3 minutes | Warning |
| Celery queue depth | >50 pending tasks | Warning |
| GitHub API circuit open | Circuit breaker opened | Critical |
| DLQ growing | >10 items in dead letter queue | Warning |

---

## 15. Security Model

### 15.1 Security Layers

```
Layer 1: Network
  └── Cloud Run: HTTPS-only, managed TLS
  └── VPC Connector: DB/Redis not publicly accessible
  └── Cloud SQL Auth Proxy: Encrypted DB connections

Layer 2: Authentication
  └── Clerk JWT: Signed, short-lived tokens
  └── JWKS rotation: Automatic key rotation
  └── GitHub Webhook: HMAC-SHA256 signature validation
  └── Clerk Webhook: Svix signature validation

Layer 3: Authorization
  └── JWT middleware: Extract user + org context
  └── Permission checks: Role-based at route level
  └── Repository layer: org_id filter on every query

Layer 4: Data
  └── Row-level isolation: Every query scoped by org_id
  └── Encryption at rest: Cloud SQL default encryption
  └── Secrets: GCP Secret Manager (never in env vars in production)
  └── No PII in logs: structlog processors strip sensitive fields

Layer 5: Application
  └── Input validation: Pydantic schemas on all inputs
  └── Rate limiting: Redis token bucket per org
  └── CORS: Strict origin allowlist
  └── CSP headers: Content Security Policy on frontend
```

---

## 16. CI/CD Pipeline

### 16.1 CI Pipeline (on every PR)

```yaml
# .github/workflows/ci.yml
name: CI
on: [pull_request]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv run ruff check server/
      - run: uv run ruff format --check server/
      - run: uv run mypy server/

  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16 }
      redis: { image: redis:7 }
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv run pytest server/tests/ -v --cov

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd client && npm ci
      - run: cd client && npm run lint
      - run: cd client && npm run typecheck

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd client && npm ci
      - run: cd client && npm run test

  build:
    needs: [backend-lint, backend-test, frontend-lint, frontend-test]
    runs-on: ubuntu-latest
    steps:
      - run: docker build -f server/Dockerfile .
      - run: docker build -f server/Dockerfile.worker .
      - run: docker build -f client/Dockerfile .
```

### 16.2 CD Pipeline (on merge to main → staging)

```yaml
# .github/workflows/cd-staging.yml
name: Deploy to Staging
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
      - uses: google-github-actions/setup-gcloud@v2

      - name: Build and push images
        run: |
          gcloud builds submit --tag $REGISTRY/api:$SHA server/
          gcloud builds submit --tag $REGISTRY/worker:$SHA server/ -f server/Dockerfile.worker
          gcloud builds submit --tag $REGISTRY/client:$SHA client/

      - name: Deploy to Cloud Run (staging)
        run: |
          gcloud run deploy pullsense-api-staging --image $REGISTRY/api:$SHA
          gcloud run deploy pullsense-worker-staging --image $REGISTRY/worker:$SHA
          gcloud run deploy pullsense-client-staging --image $REGISTRY/client:$SHA

      - name: Run smoke tests
        run: ./scripts/smoke-test.sh $STAGING_URL
```

---

## 17. Development Phases & Milestones

### Phase 1: Foundation (Weeks 1-3)

**Goal:** User can log in, connect GitHub, and see their repositories.

| Task | Description |
|---|---|
| Project scaffolding | Next.js 15 + FastAPI + Docker Compose |
| Database schema | Alembic migrations for core tables |
| Clerk integration | Login, org support, webhook sync to PostgreSQL |
| GitHub App setup | App registration, installation flow |
| Repository management | Connect/disconnect repos, list repos |
| Basic dashboard shell | Sidebar, navigation, repo listing |
| CI pipeline | GitHub Actions for lint + test + build |

**Deliverable:** Working auth flow, GitHub App installed, repos visible in dashboard.

---

### Phase 2: Core Review Pipeline (Weeks 4-6)

**Goal:** A PR triggers a review and posts comments on GitHub.

| Task | Description |
|---|---|
| Webhook endpoint | GitHub webhook receiver with signature validation |
| Celery setup | Worker configuration, task routing, retry config |
| Triage Agent | PR classification and agent selection |
| Security Agent | Basic vulnerability detection |
| Style Agent | Coding convention checks |
| Aggregator Agent | Combine agent outputs into review |
| GitHub review posting | PR Review with inline comments |
| Review status tracking | Database status updates, basic error handling |
| SSE progress | Real-time review progress in dashboard |

**Deliverable:** End-to-end review pipeline working for a single agent + aggregator.

---

### Phase 3: Full Multi-Agent Review (Weeks 7-9)

**Goal:** All agents run in parallel with full orchestration.

| Task | Description |
|---|---|
| Test Coverage Agent | Missing test detection |
| Parallel agent execution | Celery group() for concurrent agents |
| Agent configuration | Per-repo agent enable/disable |
| Re-review support | Trigger new review from dashboard |
| Review history | List and view past reviews |
| Review findings UI | Detailed findings view with code context |
| Rate limiting | Redis token bucket per organization |
| Circuit breaker | GitHub API circuit breaker |

**Deliverable:** Full multi-agent parallel review with dashboard viewing.

---

### Phase 4: Intelligence — RAG & Memory (Weeks 10-12)

**Goal:** Reviews are context-aware using codebase RAG and memory.

| Task | Description |
|---|---|
| Pinecone setup | Index creation, namespace strategy |
| On-demand indexing | Embed changed files + related files per PR |
| Codebase Context Agent | RAG queries during review |
| Developer memory | Store and query developer preferences |
| Repository memory | Store and query repo conventions |
| Organization memory | Store and query org standards |
| Memory dashboard | View, create, delete memories |
| Memory integration | Agents use memory during reviews |

**Deliverable:** Context-aware reviews with persistent memory.

---

### Phase 5: Dashboard, Analytics & Production (Weeks 13-16)

**Goal:** Production-ready with full dashboard and analytics.

| Task | Description |
|---|---|
| Analytics dashboard | Review trends, agent stats, developer insights |
| Usage tracking | Usage events for all operations |
| Developer trends | Per-developer review patterns |
| Terraform infrastructure | Full GCP setup (staging + prod) |
| CD pipeline | Staging + production deployment |
| E2E tests | Playwright tests for critical flows |
| Error monitoring | Cloud Monitoring alerts |
| Documentation | API docs, setup guide, contributing guide |
| Security hardening | CSP headers, dependency audit, secret rotation |
| Performance optimization | Caching, query optimization, connection pooling |

**Deliverable:** Production-ready platform deployed on GCP.

---

## 18. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Gemini API rate limits** | High | High | Per-org rate limiting, queue-based backpressure, retry with backoff |
| **Review quality inconsistency** | Medium | High | Structured prompts, output validation, temperature tuning, human feedback loop |
| **Webhook delivery failures** | Medium | Medium | Idempotent processing (deduplicate by delivery_id), webhook replay from audit log |
| **RAG retrieval quality** | Medium | Medium | On-demand indexing (focused context), chunk-level optimization, re-ranking |
| **Celery worker crashes** | Low | High | `acks_late=True`, `reject_on_worker_lost=True`, health monitoring |
| **Clerk outage** | Low | Medium | JWT validation is local (JWKS cached), only sync depends on Clerk API |
| **GitHub API breaking changes** | Low | Medium | Typed API client, integration tests, version pinning |
| **Cost overrun (LLM)** | Medium | Medium | Token tracking per review, Flash for most agents, alerting on cost spikes |
| **Pinecone vendor lock-in** | Low | Low | Abstraction layer over vector operations, on-demand indexing limits data volume |

---

## 19. Future Enhancements (Post-MVP)

| Enhancement | Phase | Description |
|---|---|---|
| **GitHub Checks API** | Post-MVP | Check Runs with pass/fail status and annotations |
| **Custom agent creation** | Post-MVP | Users define custom review agents with their own prompts |
| **Auto-fix suggestions** | Post-MVP | Agents suggest code fixes, not just findings |
| **GitLab / Bitbucket support** | Future | Extend beyond GitHub |
| **Billing integration** | Future | Stripe integration for paid tiers |
| **Full repo indexing** | Future | Premium feature for deep codebase understanding |
| **Implicit memory learning** | Future | Agents learn from repeated reviewer feedback |
| **PR summary generation** | Future | Auto-generate PR descriptions from diff |
| **Slack/Discord notifications** | Future | Notify teams when reviews complete |
| **Self-hosted option** | Future | Docker Compose deployment for enterprise |
| **Model fine-tuning** | Future | Fine-tune models on team-specific review patterns |

---

## 20. Decision Log

All architectural decisions made during the design interview:

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Deployment | Cloud Run (GCP) | Serverless, scale-to-zero, Docker-native |
| 2 | Repo Structure | Monorepo (`client/` + `server/`) | Atomic commits, shared CI/CD |
| 3 | Background Workers | Celery + Redis broker | Workflow primitives (chain/group), retry support |
| 4 | ORM | SQLAlchemy 2.0 async + Alembic | Mature, async, strong migrations |
| 5 | Backend Architecture | Layered Clean Arch + domain modules | Separation of concerns, easy navigation |
| 6 | LLM Models | Flash for agents, Pro for Aggregator | Cost optimization (80% Flash) |
| 7 | Agent Selection | Hybrid (repo config + dynamic Triage) | User control + intelligent routing |
| 8 | Memory Storage | PostgreSQL (persistent) + Redis (temp) | Right tool for each access pattern |
| 9 | RAG Indexing | On-demand per PR | 100x cheaper, always fresh |
| 10 | Pricing | Free/open-source + usage tracking | Launch free, analytics-ready |
| 11 | GitHub Integration | GitHub App + installation tokens | Clean auth/integration separation |
| 12 | Webhook Processing | Immediate ACK + Celery async | GitHub 10s timeout constraint |
| 13 | Auth Sync | Clerk webhooks → PostgreSQL | No runtime Clerk dependency |
| 14 | Permissions | Clerk roles + repo-level permissions | 3 roles, simple and effective |
| 15 | Review Output | PR Review with inline comments | Best developer experience |
| 16 | Real-time Updates | Server-Sent Events (SSE) | Unidirectional, simpler than WS |
| 17 | Next.js Strategy | Server Components default | Less JS, faster loads |
| 18 | State Management | TanStack Query + Zustand | Server state + minimal client state |
| 19 | Observability | GCP Cloud Ops + structlog | Native GCP, structured logs |
| 20 | Testing | pytest + Vitest + Playwright | Full pyramid coverage |
| 21 | Error Handling | Exponential backoff + circuit breaker + DLQ | Resilient external API interaction |
| 22 | Caching | Redis with TTL-based expiration | Hot path optimization |
| 23 | Secrets | GCP Secret Manager + Pydantic Settings | Secure + fail-fast validation |
| 24 | CI/CD | GitHub Actions + Terraform + Artifact Registry | Full GitOps pipeline |
| 25 | Multi-tenancy | Row-level isolation by org_id | Industry standard, scalable |
| 26 | Phases | 5 incremental phases | Deployable increments |
| 27 | Vector DB | Pinecone Serverless | Pay-per-query, namespace isolation |
| 28 | Embeddings | Gemini text-embedding-004 | Single vendor, code-optimized |
| 29 | Theme | Dark mode default | Developer tooling standard |
| 30 | Tailwind | v4 (CSS-first) | Greenfield, latest stable |
| 31 | Python deps | uv | Already using, fastest resolver |
| 32 | Rate Limiting | Per-org Redis token bucket (100/hr) | Cost + infrastructure protection |
| 33 | Local Dev | Docker Compose | One-command full stack |
| 34 | API Contract | OpenAPI → auto-generated TS client | Single source of truth |
