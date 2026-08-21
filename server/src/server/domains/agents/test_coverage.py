"""PullSense Server — Agents: Test Coverage Agent."""

from __future__ import annotations

from typing import Any

from server.config import Settings
from server.domains.agents.base import AgentFindingList, BaseAgent
from server.domains.github.schemas import PRDiffContext


class TestCoverageAgent(BaseAgent[AgentFindingList]):
    """Test Coverage Agent (Gemini Flash) auditing test additions, mocks, and edge cases."""

    __test__ = False
    name: str = "test_coverage"
    system_prompt_filename: str = "test_coverage.md"
    temperature: float = 0.2

    def __init__(self, model_name: str | None = None, settings: Settings | None = None) -> None:
        super().__init__(model_name=model_name, settings=settings)

    def build_user_prompt(self, context: PRDiffContext, **kwargs: Any) -> str:
        file_diffs = []
        for f in context.files:
            if f.patch:
                hdr = f"### File: {f.filename} (+{f.additions}/-{f.deletions})"
                file_diffs.append(f"{hdr}\n```diff\n{f.patch}\n```")

        diff_body = "\n\n".join(file_diffs) if file_diffs else context.raw_diff[:15000]

        return f"""
# Pull Request: #{context.pr_number} - {context.title}
Repository: {context.repo_full_name}
Author: {context.author}

## Changed Files & Patches
{diff_body}

Audit the code changes for test coverage, missing assertions, untested error paths,
and mock quality.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> AgentFindingList:
        return AgentFindingList.model_validate(parsed_json)
