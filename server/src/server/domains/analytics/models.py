"""PullSense Server — Domain: Analytics models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from server.infrastructure.database import Base


class UsageEvent(Base):
    """Tracks all significant events for analytics and future billing.

    Lightweight append-only log that powers dashboard analytics:
    - Reviews per repo over time
    - Most active reviewers
    - Agent invocation counts
    - Average review duration
    """

    __tablename__ = "usage_events"

    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    repository_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100), index=True
    )  # review_started | review_completed | agent_invocation | repo_connected | etc.
    extra_metadata: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
