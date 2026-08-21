"""PullSense Server — Memory: Business logic service for memory management."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.memory.models import DeveloperMemory, OrgMemory, RepoMemory
from server.domains.memory.repository import (
    DeveloperMemoryRepository,
    OrgMemoryRepository,
    RepoMemoryRepository,
)
from server.domains.memory.schemas import (
    DeveloperMemoryResponse,
    MemoryContextBundle,
    OrgMemoryResponse,
    RepoMemoryResponse,
)
from server.infrastructure import get_logger

logger = get_logger(__name__)


class MemoryService:
    """Service coordinating 3-tier memory extraction and agent context bundling."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.org_repo = OrgMemoryRepository(session)
        self.repo_repo = RepoMemoryRepository(session)
        self.dev_repo = DeveloperMemoryRepository(session)

    async def get_review_memory_bundle(
        self,
        organization_id: str | None = None,
        repository_id: str | None = None,
        user_id: str | None = None,
    ) -> MemoryContextBundle:
        """Fetch all relevant active memories to inject into review agent prompts."""
        bundle = MemoryContextBundle()

        # 1. Organization Standards
        if organization_id:
            org_mems = await self.org_repo.list_by_org(organization_id)
            bundle.org_memories = [OrgMemoryResponse.model_validate(m) for m in org_mems]

        # 2. Repository Architectural Conventions
        if repository_id:
            repo_mems = await self.repo_repo.list_by_repo(repository_id)
            bundle.repo_memories = [RepoMemoryResponse.model_validate(m) for m in repo_mems]
            if repo_mems:
                await self.repo_repo.touch([m.id for m in repo_mems])

        # 3. Developer Style Habits & Feedback
        if user_id:
            dev_mems = await self.dev_repo.list_by_user(user_id, organization_id)
            bundle.developer_memories = [
                DeveloperMemoryResponse.model_validate(m) for m in dev_mems
            ]
            if dev_mems:
                await self.dev_repo.touch([m.id for m in dev_mems])

        logger.debug(
            "memory_bundle_assembled",
            org_count=len(bundle.org_memories),
            repo_count=len(bundle.repo_memories),
            dev_count=len(bundle.developer_memories),
        )
        return bundle

    # ── Org Memory CRUD ───────────────────────────────────────────────

    async def create_org_memory(
        self,
        organization_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
    ) -> OrgMemory:
        memory = await self.org_repo.create(
            organization_id=organization_id,
            memory_type=memory_type,
            key=key,
            value=value,
            metadata=metadata,
        )
        await self.session.commit()
        return memory

    async def list_org_memories(
        self, organization_id: str, memory_type: str | None = None
    ) -> list[OrgMemory]:
        return await self.org_repo.list_by_org(organization_id, memory_type)

    async def delete_org_memory(self, memory_id: str) -> bool:
        deleted = await self.org_repo.delete_by_id(memory_id)
        if deleted:
            await self.session.commit()
        return deleted

    # ── Repo Memory CRUD ──────────────────────────────────────────────

    async def create_repo_memory(
        self,
        repository_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
        relevance_score: float = 1.0,
    ) -> RepoMemory:
        memory = await self.repo_repo.create(
            repository_id=repository_id,
            memory_type=memory_type,
            key=key,
            value=value,
            metadata=metadata,
            relevance_score=relevance_score,
        )
        await self.session.commit()
        return memory

    async def list_repo_memories(
        self, repository_id: str, memory_type: str | None = None
    ) -> list[RepoMemory]:
        return await self.repo_repo.list_by_repo(repository_id, memory_type)

    async def delete_repo_memory(self, memory_id: str) -> bool:
        deleted = await self.repo_repo.delete_by_id(memory_id)
        if deleted:
            await self.session.commit()
        return deleted

    # ── Developer Memory CRUD ─────────────────────────────────────────

    async def create_developer_memory(
        self,
        user_id: str,
        organization_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
        relevance_score: float = 1.0,
    ) -> DeveloperMemory:
        memory = await self.dev_repo.create(
            user_id=user_id,
            organization_id=organization_id,
            memory_type=memory_type,
            key=key,
            value=value,
            metadata=metadata,
            relevance_score=relevance_score,
        )
        await self.session.commit()
        return memory

    async def list_developer_memories(
        self, user_id: str, organization_id: str | None = None
    ) -> list[DeveloperMemory]:
        return await self.dev_repo.list_by_user(user_id, organization_id)

    async def delete_developer_memory(self, memory_id: str) -> bool:
        deleted = await self.dev_repo.delete_by_id(memory_id)
        if deleted:
            await self.session.commit()
        return deleted
