"""PullSense Server — Analytics: SQLAlchemy aggregation repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.repositories.models import Repository
from server.domains.reviews.models import PullRequest, Review, ReviewAgentRun, ReviewFinding


class AnalyticsRepository:
    """Data aggregation repository for review metrics, agent performance, and trends."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_overview_aggregates(self, organization_id: str) -> dict[str, Any]:
        """Aggregate totals for reviews, findings, active repos, and execution durations."""
        # 1. Total Reviews and Avg Duration
        rev_stmt = (
            select(
                func.count(Review.id).label("total_reviews"),
                func.coalesce(func.avg(Review.duration_ms), 0).label("avg_duration_ms"),
                func.coalesce(func.sum(Review.critical_count), 0).label("total_critical"),
                func.coalesce(func.sum(Review.warning_count), 0).label("total_warning"),
                func.coalesce(func.sum(Review.suggestion_count), 0).label("total_suggestion"),
                func.coalesce(func.sum(Review.total_findings), 0).label("total_findings"),
            )
            .join(PullRequest, Review.pull_request_id == PullRequest.id)
            .join(Repository, PullRequest.repository_id == Repository.id)
            .where(Repository.organization_id == organization_id)
        )
        rev_result = (await self.session.execute(rev_stmt)).one()

        # 2. Active Repositories
        repo_stmt = select(func.count(Repository.id)).where(
            Repository.organization_id == organization_id,
            Repository.is_active == True,  # noqa: E712
        )
        active_repos = (await self.session.execute(repo_stmt)).scalar() or 0

        return {
            "total_reviews": rev_result.total_reviews or 0,
            "avg_duration_ms": int(rev_result.avg_duration_ms or 0),
            "total_critical": rev_result.total_critical or 0,
            "total_warning": rev_result.total_warning or 0,
            "total_suggestion": rev_result.total_suggestion or 0,
            "total_findings": rev_result.total_findings or 0,
            "active_repositories": active_repos,
        }

    async def get_top_categories(
        self, organization_id: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get most frequent finding categories."""
        stmt = (
            select(
                ReviewFinding.category,
                func.count(ReviewFinding.id).label("count"),
            )
            .join(Review, ReviewFinding.review_id == Review.id)
            .join(PullRequest, Review.pull_request_id == PullRequest.id)
            .join(Repository, PullRequest.repository_id == Repository.id)
            .where(Repository.organization_id == organization_id)
            .group_by(ReviewFinding.category)
            .order_by(func.count(ReviewFinding.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [{"category": row[0], "count": row[1]} for row in result.all()]

    async def get_agent_metrics(self, organization_id: str) -> list[dict[str, Any]]:
        """Get performance and token usage by agent name."""
        stmt = (
            select(
                ReviewAgentRun.agent_name,
                ReviewAgentRun.model_used,
                func.count(ReviewAgentRun.id).label("total_runs"),
                func.coalesce(func.avg(ReviewAgentRun.duration_ms), 0).label("avg_latency"),
                func.coalesce(
                    func.sum(ReviewAgentRun.input_tokens + ReviewAgentRun.output_tokens), 0
                ).label("total_tokens"),
            )
            .join(Review, ReviewAgentRun.review_id == Review.id)
            .join(PullRequest, Review.pull_request_id == PullRequest.id)
            .join(Repository, PullRequest.repository_id == Repository.id)
            .where(Repository.organization_id == organization_id)
            .group_by(ReviewAgentRun.agent_name, ReviewAgentRun.model_used)
        )
        result = await self.session.execute(stmt)
        return [
            {
                "agent_name": row[0],
                "model_used": row[1],
                "total_runs": row[2],
                "avg_latency_ms": int(row[3]),
                "total_tokens": int(row[4]),
            }
            for row in result.all()
        ]
