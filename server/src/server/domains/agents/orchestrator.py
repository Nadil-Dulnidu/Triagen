"""PullSense Server — Agents: Multi-agent pipeline orchestrator."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from server.config import Settings, get_settings
from server.domains.agents.aggregator import AggregatorAgent
from server.domains.agents.base import (
    AggregatorOutput,
    RawFinding,
    TriageOutput,
)
from server.domains.agents.codebase_context import CodebaseContextAgent
from server.domains.agents.runner import AgentExecutionResult
from server.domains.agents.security import SecurityAgent
from server.domains.agents.style import StyleAgent
from server.domains.agents.test_coverage import TestCoverageAgent
from server.domains.agents.triage import TriageAgent
from server.domains.github.schemas import PRDiffContext
from server.domains.memory.schemas import MemoryContextBundle
from server.infrastructure import get_logger

logger = get_logger(__name__)

ProgressCallback = Callable[[str, dict[str, Any]], Coroutine[Any, Any, None]]


class AgentTelemetry:
    """Telemetry data captured for an individual agent run."""

    def __init__(
        self,
        agent_name: str,
        model_used: str,
        status: str,
        duration_ms: int,
        input_tokens: int,
        output_tokens: int,
        raw_output: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        self.agent_name = agent_name
        self.model_used = model_used
        self.status = status
        self.duration_ms = duration_ms
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.raw_output = raw_output
        self.error_message = error_message


class ReviewOrchestrationResult:
    """Comprehensive result of the multi-agent review workflow."""

    def __init__(
        self,
        triage: TriageOutput,
        aggregator_output: AggregatorOutput,
        agent_telemetries: list[AgentTelemetry],
        total_tokens: int,
        total_duration_ms: int,
    ) -> None:
        self.triage = triage
        self.aggregator_output = aggregator_output
        self.agent_telemetries = agent_telemetries
        self.total_tokens = total_tokens
        self.total_duration_ms = total_duration_ms


class ReviewOrchestrator:
    """Orchestrates the multi-agent AI review workflow for a pull request."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.triage_agent = TriageAgent(settings=self.settings)
        self.security_agent = SecurityAgent(settings=self.settings)
        self.style_agent = StyleAgent(settings=self.settings)
        self.test_coverage_agent = TestCoverageAgent(settings=self.settings)
        self.codebase_context_agent = CodebaseContextAgent(settings=self.settings)
        self.aggregator_agent = AggregatorAgent(settings=self.settings)

    async def run_pipeline(
        self,
        context: PRDiffContext,
        memory_bundle: MemoryContextBundle | None = None,
        rag_snippets: list[str] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> ReviewOrchestrationResult:
        """Execute the multi-stage review pipeline: Triage -> Parallel Agents -> Aggregator."""
        import time

        start_time = time.perf_counter()
        telemetries: list[AgentTelemetry] = []

        # ── Step 1: Triage Assessment ────────────────────────────────
        if on_progress:
            await on_progress("review.triaging", {"stage": "triaging"})

        triage_output, triage_exec = await self.triage_agent.run(context)
        telemetries.append(
            AgentTelemetry(
                agent_name="triage",
                model_used=self.triage_agent.model_name,
                status="completed",
                duration_ms=triage_exec.duration_ms,
                input_tokens=triage_exec.input_tokens,
                output_tokens=triage_exec.output_tokens,
                raw_output=triage_exec.parsed_json,
            )
        )

        if on_progress:
            await on_progress(
                "review.triaged",
                {
                    "stage": "triaged",
                    "classification": triage_output.classification,
                    "risk_score": triage_output.risk_score,
                    "recommended_agents": triage_output.recommended_agents,
                },
            )

        # ── Step 2: Parallel Review Agents ───────────────────────────
        active_agents = triage_output.recommended_agents or ["security", "style", "test_coverage"]
        agent_tasks: list[Any] = []

        if "security" in active_agents:
            agent_tasks.append(
                self._run_review_agent("security", self.security_agent, context, on_progress)
            )

        if "style" in active_agents:
            agent_tasks.append(
                self._run_review_agent("style", self.style_agent, context, on_progress)
            )

        if "test_coverage" in active_agents or "tests" in active_agents:
            agent_tasks.append(
                self._run_review_agent(
                    "test_coverage", self.test_coverage_agent, context, on_progress
                )
            )

        if memory_bundle or rag_snippets or "codebase_context" in active_agents:
            agent_tasks.append(
                self._run_review_agent(
                    "codebase_context",
                    self.codebase_context_agent,
                    context,
                    on_progress,
                    memory_bundle=memory_bundle,
                    rag_snippets=rag_snippets,
                )
            )

        # Default fallback if no agents selected
        if not agent_tasks:
            agent_tasks.append(
                self._run_review_agent("security", self.security_agent, context, on_progress)
            )
            agent_tasks.append(
                self._run_review_agent("style", self.style_agent, context, on_progress)
            )

        results = await asyncio.gather(*agent_tasks, return_exceptions=True)

        collected_findings: dict[str, list[RawFinding]] = {}
        for res in results:
            if isinstance(res, Exception):
                logger.error("review_agent_failed", error=str(res))
                continue

            agent_name, findings, exec_res = res
            collected_findings[agent_name] = findings
            telemetries.append(
                AgentTelemetry(
                    agent_name=agent_name,
                    model_used=self.settings.gemini_flash_model,
                    status="completed",
                    duration_ms=exec_res.duration_ms,
                    input_tokens=exec_res.input_tokens,
                    output_tokens=exec_res.output_tokens,
                    raw_output=exec_res.parsed_json,
                )
            )

        # ── Step 3: Aggregation ──────────────────────────────────────
        if on_progress:
            await on_progress("review.aggregating", {"stage": "aggregating"})

        aggregator_output, aggregator_exec = await self.aggregator_agent.run(
            context,
            triage=triage_output,
            agent_findings=collected_findings,
        )

        telemetries.append(
            AgentTelemetry(
                agent_name="aggregator",
                model_used=self.aggregator_agent.model_name,
                status="completed",
                duration_ms=aggregator_exec.duration_ms,
                input_tokens=aggregator_exec.input_tokens,
                output_tokens=aggregator_exec.output_tokens,
                raw_output=aggregator_exec.parsed_json,
            )
        )

        total_duration_ms = int((time.perf_counter() - start_time) * 1000)
        total_tokens = sum(t.input_tokens + t.output_tokens for t in telemetries)

        if on_progress:
            await on_progress(
                "review.completed",
                {
                    "stage": "completed",
                    "total_findings": len(aggregator_output.findings),
                    "duration_ms": total_duration_ms,
                },
            )

        return ReviewOrchestrationResult(
            triage=triage_output,
            aggregator_output=aggregator_output,
            agent_telemetries=telemetries,
            total_tokens=total_tokens,
            total_duration_ms=total_duration_ms,
        )

    async def _run_review_agent(
        self,
        agent_name: str,
        agent: Any,
        context: PRDiffContext,
        on_progress: ProgressCallback | None = None,
        memory_bundle: Any | None = None,
        rag_snippets: list[str] | None = None,
    ) -> tuple[str, list[RawFinding], AgentExecutionResult]:
        if on_progress:
            await on_progress(f"agent.{agent_name}.started", {"agent": agent_name})

        if agent_name == "codebase_context":
            finding_list, exec_result = await agent.run(
                context, memory_bundle=memory_bundle, rag_snippets=rag_snippets
            )
        else:
            finding_list, exec_result = await agent.run(context)

        if on_progress:
            await on_progress(
                f"agent.{agent_name}.completed",
                {"agent": agent_name, "findings_count": len(finding_list.findings)},
            )

        return agent_name, finding_list.findings, exec_result
