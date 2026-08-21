"""PullSense Server — Reviews: Data access repository layer."""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.domains.repositories.models import Repository
from server.domains.reviews.models import (
    PullRequest,
    Review,
    ReviewAgentRun,
    ReviewFinding,
)
from server.infrastructure import get_logger

logger = get_logger(__name__)


class ReviewRepository:
    """Data access layer for Reviews, Findings, and Agent Runs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_review_by_id(self, review_id: str) -> Review | None:
        """Fetch review with its pull request, findings, and agent runs loaded."""
        stmt = (
            select(Review)
            .where(Review.id == review_id)
            .options(
                selectinload(Review.pull_request),
                selectinload(Review.findings),
                selectinload(Review.agent_runs),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_review(
        self,
        pull_request_id: str,
        webhook_event_id: str | None = None,
        status: str = "pending",
    ) -> Review:
        """Create a new review in pending status."""
        review = Review(
            pull_request_id=pull_request_id,
            webhook_event_id=webhook_event_id,
            status=status,
        )
        self._session.add(review)
        await self._session.flush()
        logger.info("review_created", review_id=review.id, pr_id=pull_request_id)
        return review

    async def update_review(self, review: Review, **kwargs: Any) -> Review:
        """Update review fields."""
        for key, value in kwargs.items():
            if hasattr(review, key):
                setattr(review, key, value)
        await self._session.flush()
        return review

    async def save_findings(
        self, review_id: str, findings: list[dict[str, Any]]
    ) -> list[ReviewFinding]:
        """Save a batch of review findings."""
        created_findings: list[ReviewFinding] = []
        for f in findings:
            finding = ReviewFinding(
                review_id=review_id,
                agent_name=f.get("agent_name", "aggregator"),
                severity=f.get("severity", "suggestion"),
                category=f.get("category"),
                file_path=f.get("file_path"),
                start_line=f.get("start_line"),
                end_line=f.get("end_line"),
                title=f.get("title", ""),
                description=f.get("description", ""),
                suggestion=f.get("suggestion"),
                code_snippet=f.get("code_snippet"),
            )
            self._session.add(finding)
            created_findings.append(finding)

        await self._session.flush()
        logger.info("findings_saved", review_id=review_id, count=len(created_findings))
        return created_findings

    async def save_agent_run(
        self,
        review_id: str,
        agent_name: str,
        model_used: str,
        status: str,
        duration_ms: int,
        input_tokens: int,
        output_tokens: int,
        raw_output: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> ReviewAgentRun:
        """Record telemetry for a single agent execution."""
        run = ReviewAgentRun(
            review_id=review_id,
            agent_name=agent_name,
            model_used=model_used,
            status=status,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            raw_output=raw_output,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def list_recent_reviews(self, limit: int = 50, offset: int = 0) -> list[Review]:
        """List most recent reviews across all repositories."""
        stmt = (
            select(Review)
            .order_by(desc(Review.created_at))
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(Review.pull_request),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class PullRequestRepository:
    """Data access layer for Pull Requests."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_repo_and_number(
        self, repository_id: str, pr_number: int
    ) -> PullRequest | None:
        """Find a PR by repository ID and PR number."""
        stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id,
            PullRequest.pr_number == pr_number,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        repository_id: str,
        github_pr_id: int,
        pr_number: int,
        title: str,
        author_github_username: str | None,
        head_sha: str,
        base_branch: str,
        head_branch: str,
        status: str = "open",
        additions: int = 0,
        deletions: int = 0,
        changed_files: int = 0,
    ) -> PullRequest:
        """Upsert a pull request record."""
        pr = await self.get_by_repo_and_number(repository_id, pr_number)
        if pr is None:
            pr = PullRequest(
                repository_id=repository_id,
                github_pr_id=github_pr_id,
                pr_number=pr_number,
                title=title,
                author_github_username=author_github_username,
                head_sha=head_sha,
                base_branch=base_branch,
                head_branch=head_branch,
                status=status,
                additions=additions,
                deletions=deletions,
                changed_files=changed_files,
            )
            self._session.add(pr)
        else:
            pr.title = title
            pr.head_sha = head_sha
            pr.base_branch = base_branch
            pr.head_branch = head_branch
            pr.status = status
            pr.additions = additions
            pr.deletions = deletions
            pr.changed_files = changed_files

        await self._session.flush()
        return pr


class RepositoryEntityRepository:
    """Data access layer for Repositories."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_github_id(self, github_repo_id: int) -> Repository | None:
        stmt = select(Repository).where(Repository.github_repo_id == github_repo_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        stmt = select(Repository).where(Repository.full_name == full_name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        organization_id: str,
        github_repo_id: int,
        full_name: str,
        name: str,
        default_branch: str = "main",
        language: str | None = None,
    ) -> Repository:
        repo = await self.get_by_github_id(github_repo_id)
        if repo is None:
            repo = Repository(
                organization_id=organization_id,
                github_repo_id=github_repo_id,
                full_name=full_name,
                name=name,
                default_branch=default_branch,
                language=language,
            )
            self._session.add(repo)
        else:
            repo.full_name = full_name
            repo.name = name
            repo.default_branch = default_branch
            if language:
                repo.language = language

        await self._session.flush()
        return repo
