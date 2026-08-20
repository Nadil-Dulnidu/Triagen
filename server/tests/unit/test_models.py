"""Unit tests for SQLAlchemy model definitions."""

from __future__ import annotations

from server.domains.analytics.models import UsageEvent  # noqa: F401
from server.domains.auth.models import Organization, OrganizationMembership, User  # noqa: F401
from server.domains.memory.models import DeveloperMemory, OrgMemory, RepoMemory  # noqa: F401
from server.domains.repositories.models import RepoConfig, RepoMember, Repository  # noqa: F401
from server.domains.reviews.models import (  # noqa: F401
    PullRequest,
    Review,
    ReviewAgentRun,
    ReviewFinding,
)
from server.domains.webhooks.models import WebhookEvent  # noqa: F401
from server.infrastructure.database import Base


def test_all_15_tables_registered() -> None:
    """Verify that all 15 core database tables are registered with Base metadata."""
    expected_tables = {
        "organizations",
        "users",
        "organization_memberships",
        "repositories",
        "repo_configs",
        "repo_members",
        "pull_requests",
        "reviews",
        "review_findings",
        "review_agent_runs",
        "webhook_events",
        "developer_memories",
        "repo_memories",
        "org_memories",
        "usage_events",
    }
    registered_tables = set(Base.metadata.tables.keys())
    assert expected_tables == registered_tables


def test_user_model_columns() -> None:
    """Verify User model has required columns."""
    user_columns = {c.name for c in User.__table__.columns}
    assert "id" in user_columns
    assert "clerk_user_id" in user_columns
    assert "email" in user_columns
    assert "metadata" in user_columns


def test_review_model_columns() -> None:
    """Verify Review model has lifecycle columns."""
    review_columns = {c.name for c in Review.__table__.columns}
    assert "status" in review_columns
    assert "triage_classification" in review_columns
    assert "total_findings" in review_columns
    assert "critical_count" in review_columns
