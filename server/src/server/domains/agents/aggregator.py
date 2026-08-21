"""PullSense Server — Agents: Aggregator Agent."""

from __future__ import annotations

import json
from typing import Any

from server.config import Settings, get_settings
from server.domains.agents.base import (
    AggregatorOutput,
    BaseAgent,
    RawFinding,
    TriageOutput,
)
from server.domains.github.schemas import PRDiffContext


class AggregatorAgent(BaseAgent[AggregatorOutput]):
    """Aggregator Agent (Gemini Pro) that synthesizes and prioritizes findings."""

    name: str = "aggregator"
    system_prompt_filename: str = "aggregator.md"
    temperature: float = 0.2

    def __init__(self, model_name: str | None = None, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        # Aggregator uses Gemini Pro by default for complex reasoning and synthesis
        pro_model = model_name or settings.gemini_pro_model
        super().__init__(model_name=pro_model, settings=settings)

    def build_user_prompt(
        self,
        context: PRDiffContext,
        triage: TriageOutput | None = None,
        agent_findings: dict[str, list[RawFinding]] | None = None,
        **kwargs: Any,
    ) -> str:
        agent_findings = agent_findings or {}
        findings_payload = {
            agent_name: [f.model_dump() for f in findings]
            for agent_name, findings in agent_findings.items()
        }

        if triage:
            triage_info = (
                f"Classification: {triage.classification}, Risk Score: {triage.risk_score}/10\n"
                f"Summary: {triage.summary}"
            )
        else:
            triage_info = "Standard review"

        return f"""
# Pull Request to Finalize: #{context.pr_number} - {context.title}
Repository: {context.repo_full_name}
Author: {context.author}
Lines: +{context.additions} / -{context.deletions} in {context.changed_files_count} files

## Triage Assessment
{triage_info}

## Findings from Specialized Agents
```json
{json.dumps(findings_payload, indent=2)}
```

De-duplicate, prioritize, and produce the final synthesized review with executive summary.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> AggregatorOutput:
        return AggregatorOutput.model_validate(parsed_json)
