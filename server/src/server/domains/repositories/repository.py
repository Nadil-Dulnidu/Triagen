"""PullSense Server — Repositories: SQLAlchemy repositories for Repositories and RepoConfig."""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.domains.repositories.models import RepoConfig, Repository


class RepositoryManagerRepository:
    """Data access repository for repository entities and their agent configurations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_org(
        self, organization_id: str, is_active: bool | None = None
    ) -> list[Repository]:
        stmt = (
            select(Repository)
            .where(Repository.organization_id == organization_id)
            .options(selectinload(Repository.config))
        )
        if is_active is not None:
            stmt = stmt.where(Repository.is_active == is_active)
        stmt = stmt.order_by(Repository.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, repository_id: str) -> Repository | None:
        stmt = (
            select(Repository)
            .where(Repository.id == repository_id)
            .options(selectinload(Repository.config))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_github_id(self, github_repo_id: int) -> Repository | None:
        stmt = (
            select(Repository)
            .where(Repository.github_repo_id == github_repo_id)
            .options(selectinload(Repository.config))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        organization_id: str,
        github_repo_id: int,
        full_name: str,
        name: str,
        default_branch: str = "main",
        language: str | None = None,
        is_active: bool = True,
    ) -> Repository:
        repo = await self.get_by_github_id(github_repo_id)
        if repo:
            repo.full_name = full_name
            repo.name = name
            repo.default_branch = default_branch
            if language:
                repo.language = language
            repo.is_active = is_active
        else:
            repo = Repository(
                organization_id=organization_id,
                github_repo_id=github_repo_id,
                full_name=full_name,
                name=name,
                default_branch=default_branch,
                language=language,
                is_active=is_active,
            )
            self.session.add(repo)
            await self.session.flush()

            # Ensure default RepoConfig is initialized
            config = RepoConfig(repository_id=repo.id)
            self.session.add(config)
            repo.config = config

        await self.session.flush()
        return repo

    async def update(
        self,
        repo: Repository,
        name: str | None = None,
        default_branch: str | None = None,
        is_active: bool | None = None,
    ) -> Repository:
        if name is not None:
            repo.name = name
        if default_branch is not None:
            repo.default_branch = default_branch
        if is_active is not None:
            repo.is_active = is_active
        await self.session.flush()
        return repo

    async def delete_by_id(self, repository_id: str) -> bool:
        stmt = delete(Repository).where(Repository.id == repository_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # ── RepoConfig Operations ─────────────────────────────────────────

    async def get_or_create_config(self, repository_id: str) -> RepoConfig:
        stmt = select(RepoConfig).where(RepoConfig.repository_id == repository_id)
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()
        if not config:
            config = RepoConfig(repository_id=repository_id)
            self.session.add(config)
            await self.session.flush()
        return config

    async def update_config(
        self,
        repository_id: str,
        security_agent_enabled: bool | None = None,
        style_agent_enabled: bool | None = None,
        test_coverage_agent_enabled: bool | None = None,
        auto_review_enabled: bool | None = None,
        custom_rules: dict[str, Any] | None = None,
        ignored_paths: list[str] | None = None,
        review_language: str | None = None,
    ) -> RepoConfig:
        config = await self.get_or_create_config(repository_id)
        if security_agent_enabled is not None:
            config.security_agent_enabled = security_agent_enabled
        if style_agent_enabled is not None:
            config.style_agent_enabled = style_agent_enabled
        if test_coverage_agent_enabled is not None:
            config.test_coverage_agent_enabled = test_coverage_agent_enabled
        if auto_review_enabled is not None:
            config.auto_review_enabled = auto_review_enabled
        if custom_rules is not None:
            config.custom_rules = custom_rules
        if ignored_paths is not None:
            config.ignored_paths = ignored_paths
        if review_language is not None:
            config.review_language = review_language
        await self.session.flush()
        return config
