"""PullSense Server — Workers: Background Celery tasks for GitHub App installation sync."""

from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import select

from server.domains.reviews.repository import RepositoryEntityRepository
from server.domains.webhooks.models import WebhookEvent
from server.infrastructure import get_logger
from server.infrastructure.celery_app import celery_app
from server.infrastructure.database import create_engine, create_session_factory

logger = get_logger(__name__)


def _run_async(coro: Any) -> Any:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="server.workers.sync_tasks.sync_github_installation",
    max_retries=2,
)
def sync_github_installation(webhook_event_id: str) -> dict[str, Any]:
    """Sync repository associations when GitHub App is installed or updated."""
    return _run_async(_execute_installation_sync(webhook_event_id))


async def _execute_installation_sync(webhook_event_id: str) -> dict[str, Any]:
    engine = create_engine()
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_event_id)
        result = await session.execute(stmt)
        webhook_event = result.scalar_one_or_none()

        if not webhook_event:
            return {"status": "error", "message": "Event not found"}

        payload = webhook_event.payload
        action = payload.get("action")
        installation = payload.get("installation", {})
        installation_id = installation.get("id")

        repo_repo = RepositoryEntityRepository(session)
        org_id = webhook_event.organization_id or "00000000-0000-0000-0000-000000000000"

        # Handle added repos
        repos_added = payload.get("repositories_added", []) or payload.get("repositories", [])
        for repo_info in repos_added:
            await repo_repo.create_or_update(
                organization_id=org_id,
                github_repo_id=repo_info.get("id"),
                full_name=repo_info.get("full_name"),
                name=repo_info.get("name"),
            )

        webhook_event.processing_status = "completed"
        await session.commit()
        logger.info(
            "github_installation_synced",
            installation_id=installation_id,
            action=action,
            repos_count=len(repos_added),
        )

        return {"status": "success", "synced_count": len(repos_added)}
