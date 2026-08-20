"""PullSense Server — Domain: Memory models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from server.infrastructure.database import Base


class DeveloperMemory(Base):
    """Persistent memory about a developer's coding patterns and preferences.

    Used by agents to personalize feedback (e.g., "this developer prefers
    functional style" or "they always forget test cleanup").
    """

    __tablename__ = "developer_memories"

    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # preference | pattern | feedback
    key: Mapped[str] = mapped_column(Text)
    value: Mapped[str] = mapped_column(Text)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RepoMemory(Base):
    """Persistent memory about a repository's conventions and architecture.

    Used by agents to understand repo-specific patterns
    (e.g., "uses hexagonal architecture", "auth is in /src/auth/").
    """

    __tablename__ = "repo_memories"

    repository_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # convention | architecture | tech_debt | decision
    key: Mapped[str] = mapped_column(Text)
    value: Mapped[str] = mapped_column(Text)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OrgMemory(Base):
    """Persistent memory about organization-wide standards and policies.

    Used by agents to enforce company-wide rules
    (e.g., "all APIs must have OpenAPI docs", "no console.log in production").
    """

    __tablename__ = "org_memories"

    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # standard | policy | compliance
    key: Mapped[str] = mapped_column(Text)
    value: Mapped[str] = mapped_column(Text)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
