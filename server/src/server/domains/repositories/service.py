"""PullSense Server — Repositories: Business logic service for repository management."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.github.client import GitHubClient
from server.domains.repositories.models import RepoConfig, Repository
from server.domains.repositories.repository import RepositoryManagerRepository
from server.domains.repositories.schemas import GitHubAvailableRepoResponse
from server.infrastructure import get_logger

logger = get_logger(__name__)


class RepositoryService:
    """Service handling repository lifecycle, GitHub app syncing, and agent configurations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = RepositoryManagerRepository(session)

    async def list_repositories(
        self, organization_id: str, is_active: bool | None = None
    ) -> list[Repository]:
        return await self.repo.list_by_org(organization_id, is_active)

    async def get_repository(self, repository_id: str) -> Repository | None:
        return await self.repo.get_by_id(repository_id)

    async def update_repository(
        self,
        repository_id: str,
        name: str | None = None,
        default_branch: str | None = None,
        is_active: bool | None = None,
    ) -> Repository | None:
        repo_entity = await self.repo.get_by_id(repository_id)
        if not repo_entity:
            return None
        updated = await self.repo.update(
            repo_entity, name=name, default_branch=default_branch, is_active=is_active
        )
        await self.session.commit()
        return updated

    async def disconnect_repository(self, repository_id: str) -> bool:
        deleted = await self.repo.delete_by_id(repository_id)
        if deleted:
            await self.session.commit()
        return deleted

    async def get_repo_config(self, repository_id: str) -> RepoConfig:
        return await self.repo.get_or_create_config(repository_id)

    async def update_repo_config(
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
        config = await self.repo.update_config(
            repository_id=repository_id,
            security_agent_enabled=security_agent_enabled,
            style_agent_enabled=style_agent_enabled,
            test_coverage_agent_enabled=test_coverage_agent_enabled,
            auto_review_enabled=auto_review_enabled,
            custom_rules=custom_rules,
            ignored_paths=ignored_paths,
            review_language=review_language,
        )
        await self.session.commit()
        return config

    async def list_available_github_repositories(
        self,
        organization_id: str,
        installation_id: int | None = None,
    ) -> list[GitHubAvailableRepoResponse]:
        """Fetch repos accessible via GitHub installation and indicate connection status."""
        connected_repos = await self.repo.list_by_org(organization_id)
        connected_github_ids = {r.github_repo_id for r in connected_repos}

        # If installation_id is provided, query GitHub API
        if installation_id:
            try:
                client = GitHubClient(installation_id)
                gh_repos = await client.list_installation_repositories()
                return [
                    GitHubAvailableRepoResponse(
                        github_repo_id=r["id"],
                        full_name=r["full_name"],
                        name=r["name"],
                        private=r.get("private", False),
                        default_branch=r.get("default_branch", "main"),
                        language=r.get("language"),
                        is_connected=r["id"] in connected_github_ids,
                    )
                    for r in gh_repos
                ]
            except Exception as e:
                logger.warning("github_list_repos_failed", error=str(e))

        # Fallback to current connected repos representation
        return [
            GitHubAvailableRepoResponse(
                github_repo_id=r.github_repo_id,
                full_name=r.full_name,
                name=r.name,
                private=False,
                default_branch=r.default_branch,
                language=r.language,
                is_connected=True,
            )
            for r in connected_repos
        ]
