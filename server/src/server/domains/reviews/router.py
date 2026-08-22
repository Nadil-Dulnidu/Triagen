"""PullSense Server — Reviews: API Router for review queries, SSE streams, and re-reviews."""

from __future__ import annotations

from typing import Any

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


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_demo_data(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Seed realistic initial PR reviews, repositories, and memory rules for testing."""
    from sqlalchemy import select

    from server.domains.auth.models import Organization
    from server.domains.memory.models import OrgMemory, RepoMemory
    from server.domains.repositories.models import RepoConfig, Repository
    from server.domains.reviews.models import PullRequest, Review, ReviewAgentRun, ReviewFinding

    # 1. Organization
    clerk_org_id = "org_demo_acme_corp"
    result = await db.execute(select(Organization).where(Organization.clerk_org_id == clerk_org_id))
    org = result.scalar_one_or_none()
    if not org:
        org = Organization(
            clerk_org_id=clerk_org_id,
            name="Acme Corporation",
            slug="acme-corp",
        )
        db.add(org)
        await db.flush()

    # 2. Repositories
    repos_data = [
        ("api-gateway", "acme-corp/api-gateway", 101, "Python"),
        ("core-service", "acme-corp/core-service", 102, "TypeScript"),
        ("billing-service", "acme-corp/billing-service", 103, "Go"),
    ]
    created_repos = []
    for name, full_name, gh_id, lang in repos_data:
        repo_result = await db.execute(select(Repository).where(Repository.github_repo_id == gh_id))
        r = repo_result.scalar_one_or_none()
        if not r:
            r = Repository(
                organization_id=org.id,
                github_repo_id=gh_id,
                name=name,
                full_name=full_name,
                language=lang,
                default_branch="main",
                is_active=True,
            )
            db.add(r)
            await db.flush()
            cfg = RepoConfig(
                repository_id=r.id,
                security_agent_enabled=True,
                style_agent_enabled=True,
                test_coverage_agent_enabled=True,
                auto_review_enabled=True,
            )
            db.add(cfg)
        created_repos.append(r)

    # 3. Memory Rules
    mem_result = await db.execute(
        select(OrgMemory).where(
            OrgMemory.organization_id == org.id,
            OrgMemory.key == "api_docs_required",
        )
    )
    if not mem_result.scalar_one_or_none():
        org_mem = OrgMemory(
            organization_id=org.id,
            memory_type="standard",
            key="api_docs_required",
            value="All public REST endpoints must include OpenAPI docstrings and type annotations.",
        )
        db.add(org_mem)

    repo_mem_res = await db.execute(
        select(RepoMemory).where(
            RepoMemory.repository_id == created_repos[0].id,
            RepoMemory.key == "clean_architecture_layers",
        )
    )
    if not repo_mem_res.scalar_one_or_none():
        repo_mem = RepoMemory(
            repository_id=created_repos[0].id,
            memory_type="architecture",
            key="clean_architecture_layers",
            value="Domain services must not directly import FastAPI schemas or database drivers.",
        )
        db.add(repo_mem)

    # 4. Pull Requests & Reviews
    pr_result = await db.execute(select(PullRequest).where(PullRequest.github_pr_id == 2001))
    pr1 = pr_result.scalar_one_or_none()
    if not pr1:
        pr1 = PullRequest(
            repository_id=created_repos[0].id,
            github_pr_id=2001,
            number=42,
            title="Implement JWT verification middleware & session validation",
            description="Adds JWT validation and route guards across all protected endpoints.",
            author="sarah-dev",
            base_branch="main",
            head_branch="feature/jwt-auth",
            head_sha="a1b2c3d4e5f6",
            state="open",
            additions=145,
            deletions=12,
            changed_files_count=3,
        )
        db.add(pr1)
        await db.flush()

        rev1 = Review(
            pull_request_id=pr1.id,
            commit_sha="a1b2c3d4e5f6",
            status="completed",
            summary=(
                "Automated review identified 1 critical security flaw (unverified JWT fallback), "
                "1 style suggestion, and 1 missing unit test scenario."
            ),
            risk_level="high",
            total_findings=3,
            critical_count=1,
            warning_count=1,
            suggestion_count=1,
            duration_ms=2100,
        )
        db.add(rev1)
        await db.flush()

        f1 = ReviewFinding(
            review_id=rev1.id,
            agent_name="security",
            severity="critical",
            category="auth_vulnerability",
            file_path="src/auth/jwt.py",
            start_line=45,
            end_line=48,
            title="Unverified JWT Expiration Fallback",
            description=(
                "The token decoder suppresses ExpiredSignatureError and falls back to unverified "
                "decoding, allowing expired tokens to bypass authentication."
            ),
            suggestion="Remove the fallback block and explicitly raise 401 Unauthorized.",
        )
        f2 = ReviewFinding(
            review_id=rev1.id,
            agent_name="test_coverage",
            severity="warning",
            category="missing_tests",
            file_path="src/auth/jwt.py",
            start_line=20,
            end_line=30,
            title="Missing Test Coverage for Expired JWT Tokens",
            description="No unit test asserts that an expired token receives an HTTP 401 response.",
            suggestion="Add test_expired_token_returns_401 in tests/test_auth.py.",
        )
        f3 = ReviewFinding(
            review_id=rev1.id,
            agent_name="style",
            severity="suggestion",
            category="clean_code",
            file_path="src/auth/middleware.py",
            start_line=12,
            end_line=15,
            title="Extract Header Constant",
            description="The header string 'Authorization' is repeated across multiple files.",
            suggestion="Define AUTH_HEADER = 'Authorization' in src/auth/constants.py.",
        )
        db.add_all([f1, f2, f3])

        run1 = ReviewAgentRun(
            review_id=rev1.id,
            agent_name="triage",
            model_used="gemini-2.5-flash",
            status="completed",
            duration_ms=350,
            input_tokens=450,
            output_tokens=120,
        )
        run2 = ReviewAgentRun(
            review_id=rev1.id,
            agent_name="security",
            model_used="gemini-2.5-flash",
            status="completed",
            duration_ms=1100,
            input_tokens=1200,
            output_tokens=340,
        )
        run3 = ReviewAgentRun(
            review_id=rev1.id,
            agent_name="aggregator",
            model_used="gemini-2.5-pro",
            status="completed",
            duration_ms=650,
            input_tokens=2100,
            output_tokens=480,
        )
        db.add_all([run1, run2, run3])

    await db.commit()
    return {
        "status": "success",
        "message": "Database seeded with sample Organization, Repositories, PRs, and Reviews.",
        "seeded_count": 1,
    }
