"""PullSense Server — Agents: Security Agent."""

from __future__ import annotations

from typing import Any

from server.domains.agents.base import AgentFindingList, BaseAgent
from server.domains.github.schemas import PRDiffContext


class SecurityAgent(BaseAgent[AgentFindingList]):
    """Security Agent that inspects PR diffs for vulnerabilities, secrets, and auth flaws."""

    name: str = "security"
    system_prompt_filename: str = "security.md"
    temperature: float = 0.1

    def build_user_prompt(self, context: PRDiffContext, **kwargs: Any) -> str:
        # Build file-by-file diff sections for precise line referencing
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
Author: {context.author}

## Changed Files & Patches
{diff_body}

Thoroughly inspect the changed lines for security vulnerabilities, secrets,
injection risks, and auth flaws.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> AgentFindingList:
        return AgentFindingList.model_validate(parsed_json)
