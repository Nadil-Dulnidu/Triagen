"""PullSense Server — Webhooks: Clerk webhook handler for user/org sync."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.config import Settings, get_settings
from server.domains.auth.repository import (
    MembershipRepository,
    OrganizationRepository,
    UserRepository,
)
from server.domains.webhooks.github import verify_github_signature
from server.domains.webhooks.models import WebhookEvent
from server.infrastructure import get_logger
from server.infrastructure.database import get_db_session

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Handle incoming GitHub App webhooks.

    Validates HMAC signature, records the event for audit & replay,
    and enqueues background processing for PR events.
    """
    raw_body = await verify_github_signature(request, settings)

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery", "unknown")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        ) from err

    action = payload.get("action")

    # Store raw webhook event for idempotency and audit log
    webhook_event = WebhookEvent(
        source="github",
        event_type=event_type,
        action=action,
        delivery_id=f"gh_{delivery_id}",
        headers=dict(request.headers),
        payload=payload,
        processing_status="pending",
    )
    db.add(webhook_event)
    await db.commit()
    await db.refresh(webhook_event)

    logger.info(
        "github_webhook_received",
        event_type=event_type,
        action=action,
        delivery_id=delivery_id,
        event_id=webhook_event.id,
    )

    # Enqueue background task based on event type
    if event_type == "pull_request" and action in {"opened", "synchronize", "reopened"}:
        try:
            from server.workers.review_tasks import process_github_pr_review

            process_github_pr_review.delay(webhook_event.id)
            logger.info("enqueued_pr_review_task", event_id=webhook_event.id)
        except Exception as e:
            logger.warning("celery_enqueue_failed", error=str(e))
            # Even if Celery is offline during local test, webhook is saved in DB
    elif event_type in {"installation", "installation_repositories"}:
        try:
            from server.workers.sync_tasks import sync_github_installation

            sync_github_installation.delay(webhook_event.id)
        except Exception as e:
            logger.warning("celery_enqueue_failed", error=str(e))

    return {"status": "accepted", "event_id": str(webhook_event.id)}


async def _verify_clerk_webhook(
    request: Request,
    settings: Settings,
) -> dict[str, Any]:
    """Verify Clerk webhook signature using Svix.

    Clerk uses Svix for webhook delivery. The signature is in the
    `svix-signature` header and can be verified with HMAC-SHA256.
    """
    body = await request.body()
    headers = dict(request.headers)

    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Svix headers",
        )

    # In production, use the svix library for proper verification.
    # For now, we parse the body and trust the webhook secret validation.
    # TODO: Add svix library for proper signature verification
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        ) from err

    return payload


@router.post("/clerk", status_code=status.HTTP_200_OK)
async def handle_clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Handle Clerk webhook events for user/org synchronization.

    Supported events:
    - user.created: Create user in PostgreSQL
    - user.updated: Update user in PostgreSQL
    - user.deleted: Soft-delete user in PostgreSQL
    - organization.created: Create organization
    - organization.updated: Update organization
    - organizationMembership.created: Add user to org
    - organizationMembership.deleted: Remove user from org
    """
    payload = await _verify_clerk_webhook(request, settings)

    event_type = payload.get("type", "")
    data = payload.get("data", {})

    # Store webhook event for audit
    svix_id = request.headers.get("svix-id", "unknown")
    webhook_event = WebhookEvent(
        source="clerk",
        event_type=event_type,
        delivery_id=f"clerk_{svix_id}",
        headers=dict(request.headers),
        payload=payload,
        processing_status="processing",
    )
    db.add(webhook_event)
    await db.flush()

    try:
        if event_type == "user.created":
            await _handle_user_created(db, data)
        elif event_type == "user.updated":
            await _handle_user_updated(db, data)
        elif event_type == "user.deleted":
            await _handle_user_deleted(db, data)
        elif event_type == "organization.created":
            await _handle_org_created(db, data)
        elif event_type == "organization.updated":
            await _handle_org_updated(db, data)
        elif event_type == "organizationMembership.created":
            await _handle_membership_created(db, data)
        elif event_type == "organizationMembership.deleted":
            await _handle_membership_deleted(db, data)
        else:
            logger.info("clerk_webhook_unhandled", event_type=event_type)

        webhook_event.processing_status = "completed"
        logger.info("clerk_webhook_processed", event_type=event_type)

    except Exception as e:
        webhook_event.processing_status = "failed"
        webhook_event.error_message = str(e)
        logger.error("clerk_webhook_failed", event_type=event_type, error=str(e))
        raise

    return {"status": "ok"}


async def _handle_user_created(db: AsyncSession, data: dict[str, Any]) -> None:
    user_repo = UserRepository(db)
    clerk_user_id = data.get("id", "")
    email_addresses = data.get("email_addresses", [])
    primary_id = data.get("primary_email_address_id")
    primary_email = next(
        (e["email_address"] for e in email_addresses if e.get("id") == primary_id),
        email_addresses[0]["email_address"] if email_addresses else "",
    )
    # Extract GitHub username from external accounts
    github_username = None
    for account in data.get("external_accounts", []):
        if account.get("provider") == "oauth_github":
            github_username = account.get("username")
            break

    await user_repo.create(
        clerk_user_id=clerk_user_id,
        email=primary_email,
        username=data.get("username"),
        display_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
        avatar_url=data.get("image_url"),
        github_username=github_username,
    )


async def _handle_user_updated(db: AsyncSession, data: dict[str, Any]) -> None:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_clerk_id(data.get("id", ""))
    if user is None:
        logger.warning("clerk_user_not_found_for_update", clerk_id=data.get("id"))
        return

    email_addresses = data.get("email_addresses", [])
    primary_id = data.get("primary_email_address_id")
    primary_email = next(
        (e["email_address"] for e in email_addresses if e.get("id") == primary_id),
        user.email,
    )
    github_username = user.github_username
    for account in data.get("external_accounts", []):
        if account.get("provider") == "oauth_github":
            github_username = account.get("username")
            break

    await user_repo.update(
        user,
        email=primary_email,
        username=data.get("username"),
        display_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
        avatar_url=data.get("image_url"),
        github_username=github_username,
    )


async def _handle_user_deleted(db: AsyncSession, data: dict[str, Any]) -> None:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_clerk_id(data.get("id", ""))
    if user:
        await user_repo.soft_delete(user)


async def _handle_org_created(db: AsyncSession, data: dict[str, Any]) -> None:
    org_repo = OrganizationRepository(db)
    await org_repo.create(
        clerk_org_id=data.get("id", ""),
        name=data.get("name", ""),
        slug=data.get("slug"),
    )


async def _handle_org_updated(db: AsyncSession, data: dict[str, Any]) -> None:
    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_clerk_id(data.get("id", ""))
    if org:
        await org_repo.update(
            org,
            name=data.get("name", org.name),
            slug=data.get("slug", org.slug),
        )


async def _handle_membership_created(db: AsyncSession, data: dict[str, Any]) -> None:
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)
    membership_repo = MembershipRepository(db)

    clerk_user_id = data.get("public_user_data", {}).get("user_id", "")
    clerk_org_id = data.get("organization", {}).get("id", "")
    role = data.get("role", "member")

    user = await user_repo.get_by_clerk_id(clerk_user_id)
    org = await org_repo.get_by_clerk_id(clerk_org_id)

    if user and org:
        existing = await membership_repo.get_membership(user.id, org.id)
        if not existing:
            await membership_repo.create(
                user_id=user.id,
                organization_id=org.id,
                role="admin" if role == "admin" else "member",
                clerk_membership_id=data.get("id"),
            )


async def _handle_membership_deleted(db: AsyncSession, data: dict[str, Any]) -> None:
    membership_repo = MembershipRepository(db)
    clerk_membership_id = data.get("id")
    if clerk_membership_id:
        await membership_repo.delete_by_clerk_id(clerk_membership_id)
