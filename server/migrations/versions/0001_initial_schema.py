"""Initial schema with all 15 core tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-20 20:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── 1. Organizations ─────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("clerk_org_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=True),
        sa.Column("github_installation_id", sa.String(255), nullable=True),
        sa.Column("review_rate_limit", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_organizations_clerk_org_id", "organizations", ["clerk_org_id"], unique=True)
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("ix_organizations_github_installation_id", "organizations", ["github_installation_id"], unique=False)

    # ── 2. Users ─────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("clerk_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("github_username", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_clerk_user_id", "users", ["clerk_user_id"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    # ── 3. Organization Memberships ──────────────────────────────────
    op.create_table(
        "organization_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("clerk_membership_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"], unique=False)
    op.create_index("ix_organization_memberships_organization_id", "organization_memberships", ["organization_id"], unique=False)
    op.create_index("ix_organization_memberships_clerk_membership_id", "organization_memberships", ["clerk_membership_id"], unique=True)

    # ── 4. Repositories ──────────────────────────────────────────────
    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("github_repo_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("default_branch", sa.String(255), nullable=False, server_default="main"),
        sa.Column("language", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_repositories_organization_id", "repositories", ["organization_id"], unique=False)
    op.create_index("ix_repositories_github_repo_id", "repositories", ["github_repo_id"], unique=True)
    op.create_index("ix_repositories_full_name", "repositories", ["full_name"], unique=False)

    # ── 5. Repo Configs ──────────────────────────────────────────────
    op.create_table(
        "repo_configs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("security_agent_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("style_agent_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("test_coverage_agent_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("auto_review_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("custom_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ignored_paths", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("review_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_repo_configs_repository_id", "repo_configs", ["repository_id"], unique=True)

    # ── 6. Repo Members ──────────────────────────────────────────────
    op.create_table(
        "repo_members",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_repo_members_repository_id", "repo_members", ["repository_id"], unique=False)
    op.create_index("ix_repo_members_user_id", "repo_members", ["user_id"], unique=False)

    # ── 7. Pull Requests ─────────────────────────────────────────────
    op.create_table(
        "pull_requests",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("github_pr_id", sa.Integer(), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author_github_username", sa.String(255), nullable=True),
        sa.Column("head_sha", sa.String(40), nullable=False),
        sa.Column("base_branch", sa.String(255), nullable=False),
        sa.Column("head_branch", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("changed_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("github_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"], unique=False)
    op.create_index("ix_pull_requests_github_pr_id", "pull_requests", ["github_pr_id"], unique=False)
    op.create_index("ix_pull_requests_status", "pull_requests", ["status"], unique=False)

    # ── 8. Webhook Events ────────────────────────────────────────────
    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=True),
        sa.Column("delivery_id", sa.String(255), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("processing_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_webhook_events_organization_id", "webhook_events", ["organization_id"], unique=False)
    op.create_index("ix_webhook_events_source", "webhook_events", ["source"], unique=False)
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"], unique=False)
    op.create_index("ix_webhook_events_delivery_id", "webhook_events", ["delivery_id"], unique=True)
    op.create_index("ix_webhook_events_processing_status", "webhook_events", ["processing_status"], unique=False)

    # ── 9. Reviews ───────────────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("pull_request_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("webhook_event_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("webhook_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("triage_classification", sa.String(50), nullable=True),
        sa.Column("triage_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("total_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("critical_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("suggestion_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("github_review_id", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("total_tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reviews_pull_request_id", "reviews", ["pull_request_id"], unique=False)
    op.create_index("ix_reviews_status", "reviews", ["status"], unique=False)

    # ── 10. Review Findings ──────────────────────────────────────────
    op.create_table(
        "review_findings",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("review_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=True),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_review_findings_review_id", "review_findings", ["review_id"], unique=False)
    op.create_index("ix_review_findings_agent_name", "review_findings", ["agent_name"], unique=False)
    op.create_index("ix_review_findings_severity", "review_findings", ["severity"], unique=False)

    # ── 11. Review Agent Runs ────────────────────────────────────────
    op.create_table(
        "review_agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("review_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(50), nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_review_agent_runs_review_id", "review_agent_runs", ["review_id"], unique=False)
    op.create_index("ix_review_agent_runs_agent_name", "review_agent_runs", ["agent_name"], unique=False)

    # ── 12. Developer Memories ───────────────────────────────────────
    op.create_table(
        "developer_memories",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_developer_memories_user_id", "developer_memories", ["user_id"], unique=False)
    op.create_index("ix_developer_memories_organization_id", "developer_memories", ["organization_id"], unique=False)
    op.create_index("ix_developer_memories_memory_type", "developer_memories", ["memory_type"], unique=False)

    # ── 13. Repo Memories ────────────────────────────────────────────
    op.create_table(
        "repo_memories",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_repo_memories_repository_id", "repo_memories", ["repository_id"], unique=False)
    op.create_index("ix_repo_memories_memory_type", "repo_memories", ["memory_type"], unique=False)

    # ── 14. Org Memories ─────────────────────────────────────────────
    op.create_table(
        "org_memories",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_org_memories_organization_id", "org_memories", ["organization_id"], unique=False)
    op.create_index("ix_org_memories_memory_type", "org_memories", ["memory_type"], unique=False)

    # ── 15. Usage Events ─────────────────────────────────────────────
    op.create_table(
        "usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("repositories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_usage_events_organization_id", "usage_events", ["organization_id"], unique=False)
    op.create_index("ix_usage_events_repository_id", "usage_events", ["repository_id"], unique=False)
    op.create_index("ix_usage_events_event_type", "usage_events", ["event_type"], unique=False)
    op.create_index("ix_usage_events_created_at", "usage_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("usage_events")
    op.drop_table("org_memories")
    op.drop_table("repo_memories")
    op.drop_table("developer_memories")
    op.drop_table("review_agent_runs")
    op.drop_table("review_findings")
    op.drop_table("reviews")
    op.drop_table("webhook_events")
    op.drop_table("pull_requests")
    op.drop_table("repo_members")
    op.drop_table("repo_configs")
    op.drop_table("repositories")
    op.drop_table("organization_memberships")
    op.drop_table("users")
    op.drop_table("organizations")
