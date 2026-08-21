"""PullSense Server — GitHub: Pydantic schemas for GitHub API and Webhooks."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ── Webhook Payloads ──────────────────────────────────────────────────


class GitHubUser(BaseModel):
    """GitHub user in webhook/API payloads."""

    id: int
    login: str
    avatar_url: str | None = None
    html_url: str | None = None


class GitHubRepo(BaseModel):
    """GitHub repository in webhook/API payloads."""

    id: int
    name: str
    full_name: str  # owner/repo
    private: bool = False
    default_branch: str = "main"
    html_url: str | None = None
    language: str | None = None
    owner: GitHubUser


class GitHubBranchRef(BaseModel):
    """Git branch reference in pull request."""

    ref: str
    sha: str
    repo: GitHubRepo | None = None


class GitHubPullRequest(BaseModel):
    """GitHub Pull Request payload."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str = "open"  # open | closed
    user: GitHubUser
    head: GitHubBranchRef
    base: GitHubBranchRef
    merged: bool = False
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    html_url: str | None = None


class GitHubInstallation(BaseModel):
    """GitHub App installation reference."""

    id: int
    account: GitHubUser | None = None


class GitHubPRWebhookPayload(BaseModel):
    """Payload for 'pull_request' webhook event."""

    action: str  # opened | synchronize | reopened | closed | etc.
    number: int
    pull_request: GitHubPullRequest
    repository: GitHubRepo
    installation: GitHubInstallation | None = None
    sender: GitHubUser | None = None


class GitHubInstallationWebhookPayload(BaseModel):
    """Payload for 'installation' and 'installation_repositories' webhook events."""

    action: str  # created | deleted | added | removed
    installation: GitHubInstallation
    repositories: list[GitHubRepo] = Field(default_factory=list)
    repositories_added: list[GitHubRepo] = Field(default_factory=list)
    repositories_removed: list[GitHubRepo] = Field(default_factory=list)
    sender: GitHubUser | None = None


# ── File and Diff Schemas ─────────────────────────────────────────────


class GitHubFileChange(BaseModel):
    """A changed file in a pull request."""

    sha: str | None = None
    filename: str
    status: str = "modified"  # added | modified | removed | renamed
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    patch: str | None = None  # Diff hunk
    raw_url: str | None = None
    contents_url: str | None = None


class PRDiffContext(BaseModel):
    """Consolidated PR context used by AI review agents."""

    repo_full_name: str
    pr_number: int
    title: str
    description: str
    author: str
    base_branch: str
    head_branch: str
    head_sha: str
    additions: int
    deletions: int
    changed_files_count: int
    files: list[GitHubFileChange]
    raw_diff: str = ""


# ── Review Posting Schemas ────────────────────────────────────────────


class InlineComment(BaseModel):
    """An inline comment to attach to a GitHub PR Review."""

    path: str
    line: int
    body: str


class GitHubReviewPayload(BaseModel):
    """Payload for POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews."""

    commit_id: str | None = None
    body: str
    event: str = "COMMENT"  # COMMENT | APPROVE | REQUEST_CHANGES
    comments: list[InlineComment] = Field(default_factory=list)
