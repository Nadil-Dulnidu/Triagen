"""PullSense Server — Memory: Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ── Org Memory Schemas ────────────────────────────────────────────────


class CreateOrgMemoryRequest(BaseModel):
    """Payload to create an organization-wide standard or compliance memory."""

    memory_type: str = Field(
        ...,
        description="Type of memory: standard | policy | compliance",
        examples=["standard"],
    )
    key: str = Field(..., description="Short identifier or topic", examples=["api_docs"])
    value: str = Field(
        ...,
        description="Instruction or standard rule",
        examples=["All public REST endpoints must include OpenAPI docstrings."],
    )
    metadata: dict[str, Any] | None = None


class OrgMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    memory_type: str
    key: str
    value: str
    metadata: dict[str, Any] | None = Field(default=None, alias="extra_metadata")
    created_at: datetime
    updated_at: datetime


# ── Repo Memory Schemas ───────────────────────────────────────────────


class CreateRepoMemoryRequest(BaseModel):
    """Payload to create a repository architectural convention memory."""

    memory_type: str = Field(
        ...,
        description="Type of memory: convention | architecture | tech_debt | decision",
        examples=["architecture"],
    )
    key: str = Field(..., description="Short topic", examples=["folder_structure"])
    value: str = Field(
        ...,
        description="Convention rule",
        examples=["Follow Clean Architecture: domain models must not import from infrastructure."],
    )
    metadata: dict[str, Any] | None = None
    relevance_score: float = 1.0


class RepoMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    memory_type: str
    key: str
    value: str
    metadata: dict[str, Any] | None = Field(default=None, alias="extra_metadata")
    relevance_score: float
    last_accessed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ── Developer Memory Schemas ──────────────────────────────────────────


class CreateDeveloperMemoryRequest(BaseModel):
    """Payload to create a developer preference memory."""

    memory_type: str = Field(
        ...,
        description="Type of memory: preference | pattern | feedback",
        examples=["preference"],
    )
    key: str = Field(..., description="Short topic", examples=["async_patterns"])
    value: str = Field(
        ...,
        description="Preference detail",
        examples=["Prefers async/await syntax and explicit exception types over bare except."],
    )
    metadata: dict[str, Any] | None = None
    relevance_score: float = 1.0


class DeveloperMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    organization_id: str
    memory_type: str
    key: str
    value: str
    metadata: dict[str, Any] | None = Field(default=None, alias="extra_metadata")
    relevance_score: float
    last_accessed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ── Aggregated Memory Bundle ─────────────────────────────────────────


class MemoryContextBundle(BaseModel):
    """Bundle of active memories injected into agent prompts during review."""

    org_memories: list[OrgMemoryResponse] = Field(default_factory=list)
    repo_memories: list[RepoMemoryResponse] = Field(default_factory=list)
    developer_memories: list[DeveloperMemoryResponse] = Field(default_factory=list)

    def format_as_prompt_section(self) -> str:
        """Format memories into a markdown block for LLM prompts."""
        sections: list[str] = []

        if self.org_memories:
            sections.append("### Organization Standards & Policies")
            for m in self.org_memories:
                sections.append(f"- **[{m.key}]**: {m.value}")

        if self.repo_memories:
            sections.append("\n### Repository Architecture & Conventions")
            for m in self.repo_memories:
                sections.append(f"- **[{m.key}]**: {m.value}")

        if self.developer_memories:
            sections.append("\n### Developer Preferences & Style Habits")
            for m in self.developer_memories:
                sections.append(f"- **[{m.key}]**: {m.value}")

        return "\n".join(sections) if sections else "No custom memory rules configured."
