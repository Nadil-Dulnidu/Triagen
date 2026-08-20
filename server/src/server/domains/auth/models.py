"""PullSense Server — Domain: Auth models (User, Organization, Membership)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.infrastructure.database import Base


class Organization(Base):
    """A Clerk organization synced to PostgreSQL.

    Serves as the top-level tenant for multi-tenancy isolation.
    All tenant-scoped data references this via organization_id.
    """

    __tablename__ = "organizations"

    clerk_org_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    github_installation_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    review_rate_limit: Mapped[int] = mapped_column(default=100)
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    repositories: Mapped[list[Repository]] = relationship(  # noqa: F821
        back_populates="organization", cascade="all, delete-orphan"
    )


class User(Base):
    """A Clerk user synced to PostgreSQL.

    The internal user_id (UUID) is used for all foreign keys,
    never the Clerk user ID directly.
    """

    __tablename__ = "users"

    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True, default=dict
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class OrganizationMembership(Base):
    """Maps users to organizations with a role (admin or member)."""

    __tablename__ = "organization_memberships"

    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), default="member")  # admin | member
    clerk_membership_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")
