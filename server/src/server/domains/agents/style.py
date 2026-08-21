"""PullSense Server — Agents: Style & Maintainability Agent."""

from __future__ import annotations

from typing import Any

from server.domains.agents.base import AgentFindingList, BaseAgent
from server.domains.github.schemas import PRDiffContext


class StyleAgent(BaseAgent[AgentFindingList]):
    """Style Agent that analyzes code maintainability, clean code patterns, and idioms."""

    name: str = "style"
    system_prompt_filename: str = "style.md"
    temperature: float = 0.2

    def build_user_prompt(self, context: PRDiffContext, **kwargs: Any) -> str:
        file_diffs: list[str] = []
        for file in context.files:
            if file.patch:
                file_diffs.append(
                    f"### File: `{file.filename}` ({file.status})\n```diff\n{file.patch}\n```"
                )

        diff_body = "\n\n".join(file_diffs) if file_diffs else context.raw_diff[:15000]

        return f"""
# Pull Request: #{context.pr_number} - {context.title}
Repository: {context.repo_full_name}

## Description
{context.description or "No description."}

## Changed Files & Patches
{diff_body}

Review the code changes for maintainability, idiomatic patterns,
naming clarity, and architectural cleanliness.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> AgentFindingList:
        return AgentFindingList.model_validate(parsed_json)
