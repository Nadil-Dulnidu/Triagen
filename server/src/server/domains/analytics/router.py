"""PullSense Server — Analytics: REST API Router for organization metrics and trends."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.analytics.schemas import (
    AgentPerformanceMetric,
    AnalyticsOverviewResponse,
    CategoryHotspot,
)
from server.domains.analytics.service import AnalyticsService
from server.domains.auth.middleware import get_auth_context
from server.domains.auth.schemas import AuthContext
from server.infrastructure.database import get_db_session

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> AnalyticsOverviewResponse:
    """Get high-level organization review velocity, time saved, and quality metrics."""
    org_id = auth.organization_id or "00000000-0000-0000-0000-000000000000"
    service = AnalyticsService(db)
    return await service.get_overview(org_id)


@router.get("/agents", response_model=list[AgentPerformanceMetric])
async def get_agent_performance(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[AgentPerformanceMetric]:
    """Get AI review agent execution metrics and token usage."""
    org_id = auth.organization_id or "00000000-0000-0000-0000-000000000000"
    service = AnalyticsService(db)
    overview = await service.get_overview(org_id)
    return overview.agent_performance


@router.get("/categories", response_model=list[CategoryHotspot])
async def get_top_categories(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[CategoryHotspot]:
    """Get top finding categories and issue hotspots."""
    org_id = auth.organization_id or "00000000-0000-0000-0000-000000000000"
    service = AnalyticsService(db)
    overview = await service.get_overview(org_id)
    return overview.top_categories
