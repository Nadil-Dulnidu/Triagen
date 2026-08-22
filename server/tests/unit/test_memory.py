"""Unit tests for Memory domain repositories and MemoryService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from server.domains.memory.models import OrgMemory, RepoMemory
from server.domains.memory.repository import (
    OrgMemoryRepository,
    RepoMemoryRepository,
)
from server.domains.memory.schemas import MemoryContextBundle, OrgMemoryResponse
from server.domains.memory.service import MemoryService


@pytest.mark.asyncio
async def test_org_memory_crud() -> None:
    session = AsyncMock()
    session.add = MagicMock()
    repo = OrgMemoryRepository(session)

    mem = await repo.create(
        organization_id="org-1",
        memory_type="standard",
        key="api_docs",
        value="All endpoints require docstrings",
    )
    assert mem.key == "api_docs"
    assert mem.organization_id == "org-1"
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_repo_memory_touch() -> None:
    session = AsyncMock()
    sample_mem = RepoMemory(
        id="m-1",
        repository_id="repo-1",
        memory_type="architecture",
        key="clean_arch",
        value="Use repository pattern",
    )
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[sample_mem])))
    )

    repo = RepoMemoryRepository(session)
    await repo.touch(["m-1"])
    assert sample_mem.last_accessed_at is not None


@pytest.mark.asyncio
async def test_memory_context_bundle_formatting() -> None:
    bundle = MemoryContextBundle(
        org_memories=[
            OrgMemoryResponse(
                id="1",
                organization_id="org-1",
                memory_type="standard",
                key="doc_rule",
                value="Document all schemas",
                created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )
        ]
    )

    prompt_text = bundle.format_as_prompt_section()
    assert "Organization Standards" in prompt_text
    assert "doc_rule" in prompt_text
    assert "Document all schemas" in prompt_text


@pytest.mark.asyncio
async def test_memory_service_bundle_assembly() -> None:
    session = AsyncMock()
    service = MemoryService(session)

    # Mock list calls
    service.org_repo.list_by_org = AsyncMock(
        return_value=[
            OrgMemory(
                id="org-m1",
                organization_id="org-123",
                memory_type="policy",
                key="sec_policy",
                value="No hardcoded secrets",
                created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )
        ]
    )
    service.repo_repo.list_by_repo = AsyncMock(return_value=[])
    service.dev_repo.list_by_user = AsyncMock(return_value=[])

    bundle = await service.get_review_memory_bundle(
        organization_id="org-123",
        repository_id="repo-456",
    )
    assert len(bundle.org_memories) == 1
    assert bundle.org_memories[0].key == "sec_policy"
