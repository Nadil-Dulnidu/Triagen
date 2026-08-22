"""PullSense Server — Domain: Repository models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.infrastructure.database import Base


class Repository(Base):
    """A GitHub repository connected to PullSense.

    Scoped to an organization for multi-tenancy.
    """

    __tablename__ = "repositories"

    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)  # owner/repo
    name: Mapped[str] = mapped_column(String(255))
    default_branch: Mapped[str] = mapped_column(String(255), default="main")
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organization: Mapped[Organization] = relationship(  # noqa: F821
        back_populates="repositories"
    )
    config: Mapped[RepoConfig | None] = relationship(
        back_populates="repository",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    members: Mapped[list[RepoMember]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    pull_requests: Mapped[list[PullRequest]] = relationship(  # noqa: F821
        back_populates="repository", cascade="all, delete-orphan"
    )


class RepoConfig(Base):
    """Per-repository configuration for AI agents and review behavior."""

    __tablename__ = "repo_configs"

    repository_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    security_agent_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    style_agent_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    test_coverage_agent_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_review_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    custom_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    ignored_paths: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    review_language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="config")


class RepoMember(Base):
    """Repository-level member with role (admin or member)."""

    __tablename__ = "repo_members"

    repository_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), default="member")  # admin | member
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="members")
    user: Mapped[User] = relationship()  # noqa: F821
