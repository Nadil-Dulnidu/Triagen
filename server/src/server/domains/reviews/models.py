"""PullSense Server — Domain: Review models (PullRequest, Review, Findings, AgentRuns)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.infrastructure.database import Base


class PullRequest(Base):
    """A GitHub Pull Request tracked by PullSense."""

    __tablename__ = "pull_requests"

    repository_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
    )
    github_pr_id: Mapped[int] = mapped_column(BigInteger, index=True)
    pr_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    author_github_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    head_sha: Mapped[str] = mapped_column(String(40))
    base_branch: Mapped[str] = mapped_column(String(255))
    head_branch: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(50), default="open", index=True
    )  # open | closed | merged
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, default=0)
    github_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    repository: Mapped[Repository] = relationship(  # noqa: F821
        back_populates="pull_requests"
    )
    reviews: Mapped[list[Review]] = relationship(
        back_populates="pull_request", cascade="all, delete-orphan"
    )


class Review(Base):
    """A PullSense AI review of a pull request.

    Tracks the full lifecycle: pending -> triaging -> reviewing
    -> aggregating -> posting -> completed/failed.
    """

    __tablename__ = "reviews"

    pull_request_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        index=True,
    )
    webhook_event_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("webhook_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
    )  # pending | triaging | reviewing | aggregating | posting | completed | failed
    triage_classification: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # small | medium | large | critical
    triage_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    suggestion_count: Mapped[int] = mapped_column(Integer, default=0)
    github_review_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pull_request: Mapped[PullRequest] = relationship(
        back_populates="reviews", lazy="selectin"
    )
    findings: Mapped[list[ReviewFinding]] = relationship(
        back_populates="review", cascade="all, delete-orphan", lazy="selectin"
    )
    agent_runs: Mapped[list[ReviewAgentRun]] = relationship(
        back_populates="review", cascade="all, delete-orphan", lazy="selectin"
    )


class ReviewFinding(Base):
    """An individual finding from an agent within a review.

    Each finding is tied to a specific file and line range,
    enabling inline PR comments on GitHub.
    """

    __tablename__ = "review_findings"

    review_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(
        String(50), index=True
    )  # security | style | test_coverage | codebase_context
    severity: Mapped[str] = mapped_column(
        String(50), index=True
    )  # critical | warning | suggestion | info
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    review: Mapped[Review] = relationship(back_populates="findings")


class ReviewAgentRun(Base):
    """Telemetry for a single agent's execution within a review.

    Tracks per-agent latency, token usage, status, and raw output
    for debugging and cost analysis.
    """

    __tablename__ = "review_agent_runs"

    review_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(50), index=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending | running | completed | failed
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    raw_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    review: Mapped[Review] = relationship(back_populates="agent_runs")
