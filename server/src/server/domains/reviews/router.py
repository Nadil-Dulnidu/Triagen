"""PullSense Server — Reviews: API Router for review queries, SSE streams, and re-reviews."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.auth.middleware import get_auth_context
from server.domains.auth.schemas import AuthContext
from server.domains.reviews.repository import ReviewRepository
from server.domains.reviews.schemas import (
    PullRequestResponse,
    ReviewAgentRunResponse,
    ReviewDetailResponse,
    ReviewFindingResponse,
    ReviewResponse,
)
from server.infrastructure.database import get_db_session
from server.infrastructure.sse import stream_review_events

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("", response_model=list[ReviewResponse])
async def list_reviews(
    limit: int = 50,
    offset: int = 0,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[ReviewResponse]:
    """List recent code reviews."""
    repo = ReviewRepository(db)
    reviews = await repo.list_recent_reviews(limit=limit, offset=offset)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.get("/{review_id}", response_model=ReviewDetailResponse)
async def get_review_detail(
    review_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewDetailResponse:
    """Get comprehensive review details including PR metadata, findings, and agent runs."""
    repo = ReviewRepository(db)
    review = await repo.get_review_by_id(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    # Format findings and agent runs
    findings_resp = [ReviewFindingResponse.model_validate(f) for f in (review.findings or [])]
    runs_resp = [ReviewAgentRunResponse.model_validate(r) for r in (review.agent_runs or [])]
    pr_resp = (
        PullRequestResponse.model_validate(review.pull_request) if review.pull_request else None
    )

    return ReviewDetailResponse(
        id=review.id,
        pull_request_id=review.pull_request_id,
        status=review.status,
        triage_classification=review.triage_classification,
        triage_metadata=review.triage_metadata,
        summary=review.summary,
        total_findings=review.total_findings,
        critical_count=review.critical_count,
        warning_count=review.warning_count,
        suggestion_count=review.suggestion_count,
        github_review_id=review.github_review_id,
        duration_ms=review.duration_ms,
        total_tokens_used=review.total_tokens_used,
        started_at=review.started_at,
        completed_at=review.completed_at,
        created_at=review.created_at,
        pull_request=pr_resp,
        findings=findings_resp,
        agent_runs=runs_resp,
    )


@router.get("/{review_id}/stream")
async def stream_review_progress(
    review_id: str,
) -> StreamingResponse:
    """Server-Sent Events (SSE) endpoint streaming real-time review progress events."""
    return StreamingResponse(
        stream_review_events(review_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{review_id}/re-review", status_code=status.HTTP_202_ACCEPTED)
async def trigger_re_review(
    review_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Trigger a re-review of a pull request."""
    repo = ReviewRepository(db)
    review = await repo.get_review_by_id(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    if not review.webhook_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot re-review without original webhook event",
        )

    from server.workers.review_tasks import process_github_pr_review

    process_github_pr_review.delay(review.webhook_event_id)

    return {"status": "accepted", "message": "Re-review initiated"}
