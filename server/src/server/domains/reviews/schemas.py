"""PullSense Server — Reviews: Pydantic response and request schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReviewFindingResponse(BaseModel):
    """Public finding representation returned by API."""

    id: str
    agent_name: str
    severity: str
    category: str | None = None
    file_path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    title: str
    description: str
    suggestion: str | None = None
    code_snippet: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewAgentRunResponse(BaseModel):
    """Telemetry representation for an individual agent run."""

    id: str
    agent_name: str
    model_used: str | None = None
    status: str
    duration_ms: int | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class RepositoryBriefResponse(BaseModel):
    """Brief repository representation attached to pull requests."""

    id: str
    github_repo_id: int
    full_name: str
    name: str
    default_branch: str = "main"
    language: str | None = None

    model_config = {"from_attributes": True}


class PullRequestResponse(BaseModel):
    """Pull Request metadata."""

    id: str
    github_pr_id: int
    pr_number: int
    number: int | None = None
    title: str
    author_github_username: str | None = None
    author: str | None = None
    head_sha: str
    base_branch: str
    head_branch: str
    status: str
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    created_at: datetime
    repository: RepositoryBriefResponse | None = None

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    """Public review summary representation."""

    id: str
    pull_request_id: str
    status: str
    triage_classification: str | None = None
    risk_level: str | None = None
    triage_metadata: dict[str, Any] | None = None
    summary: str | None = None
    total_findings: int = 0
    critical_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0
    github_review_id: int | None = None
    duration_ms: int | None = None
    total_tokens_used: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    pull_request: PullRequestResponse | None = None

    model_config = {"from_attributes": True}


class ReviewDetailResponse(ReviewResponse):
    """Detailed review response with findings, agent runs, and PR metadata."""

    findings: list[ReviewFindingResponse] = []
    agent_runs: list[ReviewAgentRunResponse] = []
