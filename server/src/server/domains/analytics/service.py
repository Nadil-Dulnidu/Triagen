"""PullSense Server — Analytics: Business logic service for metrics calculation."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.analytics.repository import AnalyticsRepository
from server.domains.analytics.schemas import (
    AgentPerformanceMetric,
    AnalyticsOverviewResponse,
    CategoryHotspot,
    SeverityDistribution,
)
from server.infrastructure import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service calculating aggregated metrics and trends for organizations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    async def get_overview(self, organization_id: str) -> AnalyticsOverviewResponse:
        """Calculate high-level organization review velocity and quality metrics."""
        data = await self.repo.get_overview_aggregates(organization_id)
        categories_data = await self.repo.get_top_categories(organization_id, limit=5)
        agent_data = await self.repo.get_agent_metrics(organization_id)

        # Developer hours saved heuristic: 0.5 hours (30 min) saved per automated AI review
        hours_saved = round(data["total_reviews"] * 0.5, 1)
        avg_latency_s = round(data["avg_duration_ms"] / 1000.0, 2)

        return AnalyticsOverviewResponse(
            total_reviews=data["total_reviews"],
            active_repositories=data["active_repositories"],
            total_findings_caught=data["total_findings"],
            critical_vulnerabilities_prevented=data["total_critical"],
            developer_hours_saved=hours_saved,
            avg_review_latency_seconds=avg_latency_s,
            severity_distribution=SeverityDistribution(
                critical=data["total_critical"],
                warning=data["total_warning"],
                suggestion=data["total_suggestion"],
            ),
            top_categories=[
                CategoryHotspot(category=c["category"], count=c["count"]) for c in categories_data
            ],
            agent_performance=[
                AgentPerformanceMetric(
                    agent_name=a["agent_name"],
                    model_used=a["model_used"],
                    total_runs=a["total_runs"],
                    avg_latency_ms=a["avg_latency_ms"],
                    total_tokens=a["total_tokens"],
                )
                for a in agent_data
            ],
        )
