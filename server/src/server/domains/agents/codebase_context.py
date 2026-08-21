"""PullSense Server — Agents: Codebase Context & Architectural RAG Agent."""

from __future__ import annotations

from typing import Any

from server.config import Settings
from server.domains.agents.base import AgentFindingList, BaseAgent
from server.domains.github.schemas import PRDiffContext
from server.domains.memory.schemas import MemoryContextBundle


class CodebaseContextAgent(BaseAgent[AgentFindingList]):
    """Codebase Context Agent (Gemini Flash) examining architectural consistency and RAG context."""

    name: str = "codebase_context"
    system_prompt_filename: str = "codebase_context.md"
    temperature: float = 0.1

    def __init__(self, model_name: str | None = None, settings: Settings | None = None) -> None:
        super().__init__(model_name=model_name, settings=settings)

    def build_user_prompt(
        self,
        context: PRDiffContext,
        memory_bundle: MemoryContextBundle | None = None,
        rag_snippets: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        file_diffs = []
        for f in context.files:
            if f.patch:
                hdr = f"### File: {f.filename} (+{f.additions}/-{f.deletions})"
                file_diffs.append(f"{hdr}\n```diff\n{f.patch}\n```")

        diff_body = "\n\n".join(file_diffs) if file_diffs else context.raw_diff[:15000]

        # Format Memory Rules
        memory_section = (
            memory_bundle.format_as_prompt_section()
            if memory_bundle
            else "No team memories configured."
        )

        # Format RAG Codebase Snippets
        if rag_snippets:
            rag_section = "\n\n".join([f"```\n{snippet}\n```" for snippet in rag_snippets[:5]])
        else:
            rag_section = "No external codebase vectors retrieved."

        return f"""
# Pull Request: #{context.pr_number} - {context.title}
Repository: {context.repo_full_name}
Author: {context.author}

## Active Team Standards & Architectural Conventions
{memory_section}

## Retrieved Codebase Context (Semantic Search RAG)
{rag_section}

## Changed Files & Patches
{diff_body}

Evaluate whether the pull request obeys team architecture patterns and
leverages existing codebase utilities.
"""

    def parse_output(self, parsed_json: dict[str, Any]) -> AgentFindingList:
        return AgentFindingList.model_validate(parsed_json)
