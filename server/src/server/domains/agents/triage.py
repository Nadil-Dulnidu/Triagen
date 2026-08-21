"""PullSense Server — Agents: Triage Agent."""

from __future__ import annotations

from typing import Any

from server.domains.agents.base import BaseAgent, TriageOutput
from server.domains.github.schemas import PRDiffContext


class TriageAgent(BaseAgent[TriageOutput]):
    """Triage Agent that classifies PR scope, risk, and recommends review agents."""

    name: str = "triage"
    system_prompt_filename: str = "triage.md"
    temperature: float = 0.1

    def build_user_prompt(self, context: PRDiffContext, **kwargs: Any) -> str:
        files_summary = "\n".join(
            f"- {f.filename} ({f.status}: +{f.additions}/-{f.deletions})"
            for f in context.files[:50]
        )

        return f"""
# Pull Request Metadata
- **Repository:** {context.repo_full_name}
- **PR #{context.pr_number}:** {context.title}
- **Author:** {context.author}
- **Branches:** {context.base_branch} <- {context.head_branch}
- **Total Lines Changed:** +{context.additions} / -{context.deletions}
- **Changed Files Count:** {context.changed_files_count}

## Description
{context.description or "No description provided."}

## Modified Files
{files_summary}

## Sample Diff Excerpt (first 200 lines)
```diff
{context.raw_diff[:5000]}
```

Analyze the PR scope and determine classification, risk score, and recommended review agents.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> TriageOutput:
        return TriageOutput.model_validate(parsed_json)
