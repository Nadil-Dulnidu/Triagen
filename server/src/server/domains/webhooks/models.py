"""PullSense Server — Domain: Webhook models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from server.infrastructure.database import Base


class WebhookEvent(Base):
    """Raw webhook event storage for audit logging and replay.

    Every webhook received (from GitHub or Clerk) is stored
    before processing for debugging and idempotency.
    """

    __tablename__ = "webhook_events"

    organization_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(50), index=True)  # github | clerk
    event_type: Mapped[str] = mapped_column(
        String(100), index=True
    )  # pull_request | installation | user.created | etc.
    action: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # opened | synchronize | created | etc.
    delivery_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )  # For idempotency
    headers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    processing_status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )  # pending | processing | completed | failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
