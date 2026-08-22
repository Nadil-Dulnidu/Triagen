"""Unit tests for Repositories domain and RepoConfig management."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from server.domains.repositories.models import RepoConfig, Repository
from server.domains.repositories.repository import RepositoryManagerRepository
from server.domains.repositories.service import RepositoryService


@pytest.mark.asyncio
async def test_repository_crud() -> None:
    session = AsyncMock()
    repo_mgr = RepositoryManagerRepository(session)

    # Test create_or_update
    repo_mgr.get_by_github_id = AsyncMock(return_value=None)
    session.add = MagicMock()

    new_repo = await repo_mgr.create_or_update(
        organization_id="org-1",
        github_repo_id=12345,
        full_name="acme/api",
        name="api",
    )
    assert new_repo.full_name == "acme/api"
    assert new_repo.github_repo_id == 12345


@pytest.mark.asyncio
async def test_repo_config_update() -> None:
    session = AsyncMock()
    sample_config = RepoConfig(
        id="cfg-1",
        repository_id="repo-1",
        security_agent_enabled=True,
        style_agent_enabled=True,
    )
    repo_mgr = RepositoryManagerRepository(session)
    repo_mgr.get_or_create_config = AsyncMock(return_value=sample_config)

    updated = await repo_mgr.update_config(
        repository_id="repo-1",
        style_agent_enabled=False,
        ignored_paths=["docs/**"],
    )
    assert not updated.style_agent_enabled
    assert updated.ignored_paths == ["docs/**"]


@pytest.mark.asyncio
async def test_repository_service_list() -> None:
    session = AsyncMock()
    service = RepositoryService(session)

    mock_repo = Repository(
        id="r-1",
        organization_id="org-1",
        github_repo_id=999,
        full_name="org/repo",
        name="repo",
    )
    service.repo.list_by_org = AsyncMock(return_value=[mock_repo])

    repos = await service.list_repositories("org-1")
    assert len(repos) == 1
    assert repos[0].name == "repo"
