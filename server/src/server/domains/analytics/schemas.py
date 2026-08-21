"""PullSense Server — Analytics: Pydantic request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SeverityDistribution(BaseModel):
    critical: int = 0
    warning: int = 0
    suggestion: int = 0
    info: int = 0


class CategoryHotspot(BaseModel):
    category: str
    count: int


class ReviewTrendPoint(BaseModel):
    date: str
    reviews_count: int
    findings_count: int


class AgentPerformanceMetric(BaseModel):
    agent_name: str
    model_used: str
    total_runs: int
    avg_latency_ms: int
    total_tokens: int


class DeveloperMetric(BaseModel):
    author: str
    total_reviews: int
    critical_count: int
    warning_count: int
    suggestion_count: int


class AnalyticsOverviewResponse(BaseModel):
    """High-level organization review metrics."""

    total_reviews: int = 0
    active_repositories: int = 0
    total_findings_caught: int = 0
    critical_vulnerabilities_prevented: int = 0
    developer_hours_saved: float = 0.0
    avg_review_latency_seconds: float = 0.0
    severity_distribution: SeverityDistribution = Field(default_factory=SeverityDistribution)
    top_categories: list[CategoryHotspot] = Field(default_factory=list)
    agent_performance: list[AgentPerformanceMetric] = Field(default_factory=list)
