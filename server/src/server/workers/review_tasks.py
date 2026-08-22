"""PullSense Server — Workers: Background Celery tasks for PR review execution."""

from __future__ import annotations

import asyncio
from datetime import UTC
from typing import Any

from sqlalchemy import select

from server.domains.agents.orchestrator import ReviewOrchestrator
from server.domains.github.client import GitHubClient
from server.domains.github.comments import post_github_review
from server.domains.reviews.repository import (
    PullRequestRepository,
    RepositoryEntityRepository,
    ReviewRepository,
)
from server.domains.webhooks.models import WebhookEvent
from server.infrastructure import get_logger
from server.infrastructure.celery_app import celery_app
from server.infrastructure.database import create_engine, create_session_factory
from server.infrastructure.sse import publish_review_event

logger = get_logger(__name__)


def _run_async(coro: Any) -> Any:
    """Helper to run async coroutines synchronously within a Celery task."""
    return asyncio.run(coro)


@celery_app.task(
    bind=True,
    name="server.workers.review_tasks.process_github_pr_review",
    max_retries=3,
    default_retry_delay=30,
)
def process_github_pr_review(self: Any, webhook_event_id: str) -> dict[str, Any]:
    """Execute the end-to-end multi-agent review pipeline for an incoming GitHub PR webhook."""
    logger.info("review_task_started", webhook_event_id=webhook_event_id)
    return _run_async(_execute_pr_review(webhook_event_id))


async def _execute_pr_review(webhook_event_id: str) -> dict[str, Any]:
    """Core async execution logic for PR review."""
    from datetime import datetime

    engine = create_engine()
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        # 1. Fetch raw webhook event
        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_event_id)
        result = await session.execute(stmt)
        webhook_event = result.scalar_one_or_none()

        if not webhook_event:
            logger.error("webhook_event_not_found", event_id=webhook_event_id)
            return {"status": "error", "message": "Webhook event not found"}

        payload = webhook_event.payload
        repo_data = payload.get("repository", {})
        pr_data = payload.get("pull_request", {})
        installation_data = payload.get("installation", {})

        repo_github_id = repo_data.get("id")
        repo_full_name = repo_data.get("full_name", "")
        repo_name = repo_data.get("name", "")
        pr_number = pr_data.get("number")
        github_pr_id = pr_data.get("id")
        installation_id = installation_data.get("id")

        if not all([repo_github_id, pr_number, installation_id]):
            logger.error(
                "invalid_pr_webhook_payload",
                repo_id=repo_github_id,
                pr_number=pr_number,
                installation_id=installation_id,
            )
            return {"status": "error", "message": "Missing required PR payload fields"}

        repo_repo = RepositoryEntityRepository(session)
        pr_repo = PullRequestRepository(session)
        review_repo = ReviewRepository(session)

        # 2. Upsert Repository & PullRequest
        repo_entity = await repo_repo.get_by_github_id(repo_github_id)
        if repo_entity is None:
            from server.domains.auth.models import Organization

            org = None
            if installation_id:
                stmt_org = select(Organization).where(
                    Organization.github_installation_id == str(installation_id)
                )
                res = await session.execute(stmt_org)
                org = res.scalar_one_or_none()

            if not org and webhook_event.organization_id:
                org = await session.get(Organization, webhook_event.organization_id)

            if not org:
                res = await session.execute(select(Organization).limit(1))
                org = res.scalar_one_or_none()

            if not org:
                org = Organization(
                    clerk_org_id=f"org_inst_{installation_id or 'default'}",
                    name="Default Organization",
                    github_installation_id=str(installation_id) if installation_id else None,
                )
                session.add(org)
                await session.flush()
            elif installation_id and not org.github_installation_id:
                org.github_installation_id = str(installation_id)
                await session.flush()

            org_id = org.id
            repo_entity = await repo_repo.create_or_update(
                organization_id=org_id,
                github_repo_id=repo_github_id,
                full_name=repo_full_name,
                name=repo_name,
                default_branch=repo_data.get("default_branch", "main"),
                language=repo_data.get("language"),
            )

        pr_entity = await pr_repo.create_or_update(
            repository_id=repo_entity.id,
            github_pr_id=github_pr_id,
            pr_number=pr_number,
            title=pr_data.get("title", ""),
            author_github_username=pr_data.get("user", {}).get("login"),
            head_sha=pr_data.get("head", {}).get("sha", ""),
            base_branch=pr_data.get("base", {}).get("ref", "main"),
            head_branch=pr_data.get("head", {}).get("ref", ""),
            status=pr_data.get("state", "open"),
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0),
            changed_files=pr_data.get("changed_files", 0),
        )

        # 3. Create Review in pending status
        review = await review_repo.create_review(
            pull_request_id=pr_entity.id,
            webhook_event_id=webhook_event.id,
            status="triaging",
        )
        review.started_at = datetime.now(UTC)
        await session.commit()

        # Progress callback for SSE broadcasting
        async def on_progress(event_type: str, data: dict[str, Any]) -> None:
            await publish_review_event(review.id, event_type, data)

        try:
            # 4. Fetch full PR Context via GitHub API
            await on_progress("review.fetching_pr", {"stage": "fetching_diff"})
            gh_client = GitHubClient(installation_id)
            owner, repo_short = repo_full_name.split("/", 1)
            pr_context = await gh_client.get_full_pr_context(owner, repo_short, pr_number)

            # 5. Fetch Team Memory Bundle (Org Standards, Repo Conventions, Developer Habits)
            from server.domains.memory.service import MemoryService

            memory_service = MemoryService(session)
            memory_bundle = await memory_service.get_review_memory_bundle(
                organization_id=repo_entity.organization_id if repo_entity else None,
                repository_id=repo_entity.id if repo_entity else None,
            )

            # 6. Run Multi-Agent Orchestrator
            orchestrator = ReviewOrchestrator()
            orch_result = await orchestrator.run_pipeline(
                pr_context,
                memory_bundle=memory_bundle,
                on_progress=on_progress,
            )

            # 6. Persist Findings & Telemetry
            findings_dicts = [f.model_dump() for f in orch_result.aggregator_output.findings]
            saved_findings = await review_repo.save_findings(review.id, findings_dicts)

            for tele in orch_result.agent_telemetries:
                await review_repo.save_agent_run(
                    review_id=review.id,
                    agent_name=tele.agent_name,
                    model_used=tele.model_used,
                    status=tele.status,
                    duration_ms=tele.duration_ms,
                    input_tokens=tele.input_tokens,
                    output_tokens=tele.output_tokens,
                    raw_output=tele.raw_output,
                    error_message=tele.error_message,
                )

            # Count severities
            critical_count = sum(1 for f in saved_findings if f.severity == "critical")
            warning_count = sum(1 for f in saved_findings if f.severity == "warning")
            suggestion_count = sum(1 for f in saved_findings if f.severity == "suggestion")

            # 7. Post Review to GitHub
            await on_progress("review.posting_to_github", {"stage": "posting_review"})
            github_review_id = await post_github_review(
                installation_id=installation_id,
                owner=owner,
                repo=repo_short,
                pr_number=pr_number,
                commit_sha=pr_entity.head_sha,
                review=review,
                findings=saved_findings,
            )

            # 8. Mark review completed
            await review_repo.update_review(
                review,
                status="completed",
                triage_classification=orch_result.triage.classification,
                triage_metadata=orch_result.triage.model_dump(),
                summary=orch_result.aggregator_output.summary,
                total_findings=len(saved_findings),
                critical_count=critical_count,
                warning_count=warning_count,
                suggestion_count=suggestion_count,
                github_review_id=github_review_id,
                duration_ms=orch_result.total_duration_ms,
                total_tokens_used=orch_result.total_tokens,
                completed_at=datetime.now(UTC),
            )

            webhook_event.processing_status = "completed"
            await session.commit()

            await on_progress(
                "review.completed",
                {
                    "stage": "completed",
                    "github_review_id": github_review_id,
                    "findings_count": len(saved_findings),
                },
            )

            logger.info(
                "review_pipeline_succeeded",
                review_id=review.id,
                pr_number=pr_number,
                total_findings=len(saved_findings),
                duration_ms=orch_result.total_duration_ms,
            )

            return {
                "status": "success",
                "review_id": review.id,
                "findings_count": len(saved_findings),
                "github_review_id": github_review_id,
            }

        except Exception as err:
            logger.error("review_pipeline_failed", review_id=review.id, error=str(err))
            await review_repo.update_review(
                review,
                status="failed",
                error_message=str(err),
                completed_at=datetime.now(UTC),
            )
            webhook_event.processing_status = "failed"
            webhook_event.error_message = str(err)
            await session.commit()

            await on_progress("review.failed", {"stage": "failed", "error": str(err)})
            raise
        finally:
            await engine.dispose()
