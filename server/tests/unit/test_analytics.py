"""Unit tests for Analytics domain and overview aggregations."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from server.domains.analytics.service import AnalyticsService


@pytest.mark.asyncio
async def test_analytics_service_overview_calculation() -> None:
    session = AsyncMock()
    service = AnalyticsService(session)

    service.repo.get_overview_aggregates = AsyncMock(
        return_value={
            "total_reviews": 50,
            "avg_duration_ms": 2500,
            "total_critical": 5,
            "total_warning": 12,
            "total_suggestion": 30,
            "total_findings": 47,
            "active_repositories": 3,
        }
    )
    service.repo.get_top_categories = AsyncMock(return_value=[{"category": "auth", "count": 10}])
    service.repo.get_agent_metrics = AsyncMock(
        return_value=[
            {
                "agent_name": "security",
                "model_used": "gemini-2.5-flash",
                "total_runs": 50,
                "avg_latency_ms": 1100,
                "total_tokens": 150000,
            }
        ]
    )

    overview = await service.get_overview("org-123")
    assert overview.total_reviews == 50
    assert overview.developer_hours_saved == 25.0  # 50 * 0.5 hours
    assert overview.avg_review_latency_seconds == 2.5
    assert overview.critical_vulnerabilities_prevented == 5
    assert len(overview.top_categories) == 1
    assert len(overview.agent_performance) == 1
