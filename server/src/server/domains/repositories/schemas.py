"""PullSense Server — Repositories: Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ── Repo Config Schemas ───────────────────────────────────────────────


class RepoConfigResponse(BaseModel):
    """Configuration options for AI review agents on a repository."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    security_agent_enabled: bool = True
    style_agent_enabled: bool = True
    test_coverage_agent_enabled: bool = True
    auto_review_enabled: bool = True
    custom_rules: dict[str, Any] | None = None
    ignored_paths: list[str] | None = None
    review_language: str = "en"
    created_at: datetime
    updated_at: datetime


class UpdateRepoConfigRequest(BaseModel):
    """Payload to update AI agent settings on a repository."""

    security_agent_enabled: bool | None = None
    style_agent_enabled: bool | None = None
    test_coverage_agent_enabled: bool | None = None
    auto_review_enabled: bool | None = None
    custom_rules: dict[str, Any] | None = None
    ignored_paths: list[str] | None = None
    review_language: str | None = None


# ── Repository Schemas ────────────────────────────────────────────────


class RepositoryResponse(BaseModel):
    """Connected repository details."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    github_repo_id: int
    full_name: str
    name: str
    default_branch: str = "main"
    language: str | None = None
    private: bool = False
    is_active: bool = True
    last_review_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    config: RepoConfigResponse | None = None


class UpdateRepoRequest(BaseModel):
    """Payload to update repository settings."""

    name: str | None = None
    default_branch: str | None = None
    is_active: bool | None = None


class ConnectRepositoriesRequest(BaseModel):
    """Payload to connect one or more GitHub repositories."""

    repository_ids: list[int] = Field(
        ...,
        description="List of GitHub repository IDs from the GitHub App installation",
    )


class GitHubAvailableRepoResponse(BaseModel):
    """Repository available from GitHub App installation."""

    github_repo_id: int
    full_name: str
    name: str
    private: bool = False
    default_branch: str = "main"
    language: str | None = None
    is_connected: bool = False
