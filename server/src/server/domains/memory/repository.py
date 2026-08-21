"""PullSense Server — Memory: SQLAlchemy repositories for Org, Repo, and Developer memories."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.memory.models import DeveloperMemory, OrgMemory, RepoMemory


class OrgMemoryRepository:
    """Data access repository for organization-wide memories."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        organization_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
    ) -> OrgMemory:
        memory = OrgMemory(
            organization_id=organization_id,
            memory_type=memory_type,
            key=key,
            value=value,
            extra_metadata=metadata,
        )
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def list_by_org(
        self, organization_id: str, memory_type: str | None = None
    ) -> list[OrgMemory]:
        stmt = select(OrgMemory).where(OrgMemory.organization_id == organization_id)
        if memory_type:
            stmt = stmt.where(OrgMemory.memory_type == memory_type)
        stmt = stmt.order_by(OrgMemory.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, memory_id: str) -> OrgMemory | None:
        stmt = select(OrgMemory).where(OrgMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, memory_id: str) -> bool:
        stmt = delete(OrgMemory).where(OrgMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class RepoMemoryRepository:
    """Data access repository for repository-specific memories."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        repository_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
        relevance_score: float = 1.0,
    ) -> RepoMemory:
        memory = RepoMemory(
            repository_id=repository_id,
            memory_type=memory_type,
            key=key,
            value=value,
            extra_metadata=metadata,
            relevance_score=relevance_score,
        )
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def list_by_repo(
        self, repository_id: str, memory_type: str | None = None
    ) -> list[RepoMemory]:
        stmt = select(RepoMemory).where(RepoMemory.repository_id == repository_id)
        if memory_type:
            stmt = stmt.where(RepoMemory.memory_type == memory_type)
        stmt = stmt.order_by(RepoMemory.relevance_score.desc(), RepoMemory.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, memory_id: str) -> RepoMemory | None:
        stmt = select(RepoMemory).where(RepoMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def touch(self, memory_ids: list[str]) -> None:
        """Update last_accessed_at timestamp for used memories."""
        if not memory_ids:
            return
        stmt = select(RepoMemory).where(RepoMemory.id.in_(memory_ids))
        result = await self.session.execute(stmt)
        now = datetime.now(UTC)
        for memory in result.scalars().all():
            memory.last_accessed_at = now

    async def delete_by_id(self, memory_id: str) -> bool:
        stmt = delete(RepoMemory).where(RepoMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class DeveloperMemoryRepository:
    """Data access repository for developer preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: str,
        organization_id: str,
        memory_type: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
        relevance_score: float = 1.0,
    ) -> DeveloperMemory:
        memory = DeveloperMemory(
            user_id=user_id,
            organization_id=organization_id,
            memory_type=memory_type,
            key=key,
            value=value,
            extra_metadata=metadata,
            relevance_score=relevance_score,
        )
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def list_by_user(
        self, user_id: str, organization_id: str | None = None
    ) -> list[DeveloperMemory]:
        stmt = select(DeveloperMemory).where(DeveloperMemory.user_id == user_id)
        if organization_id:
            stmt = stmt.where(DeveloperMemory.organization_id == organization_id)
        stmt = stmt.order_by(
            DeveloperMemory.relevance_score.desc(),
            DeveloperMemory.created_at.desc(),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, memory_id: str) -> DeveloperMemory | None:
        stmt = select(DeveloperMemory).where(DeveloperMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def touch(self, memory_ids: list[str]) -> None:
        """Update last_accessed_at timestamp for used memories."""
        if not memory_ids:
            return
        stmt = select(DeveloperMemory).where(DeveloperMemory.id.in_(memory_ids))
        result = await self.session.execute(stmt)
        now = datetime.now(UTC)
        for memory in result.scalars().all():
            memory.last_accessed_at = now

    async def delete_by_id(self, memory_id: str) -> bool:
        stmt = delete(DeveloperMemory).where(DeveloperMemory.id == memory_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
