"""PullSense Server — Repositories: REST API Router for Repositories and GitHub connections."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.auth.middleware import get_auth_context
from server.domains.auth.schemas import AuthContext
from server.domains.repositories.schemas import (
    ConnectRepositoriesRequest,
    GitHubAvailableRepoResponse,
    RepoConfigResponse,
    RepositoryResponse,
    UpdateRepoConfigRequest,
    UpdateRepoRequest,
)
from server.domains.repositories.service import RepositoryService
from server.infrastructure.database import get_db_session

router = APIRouter(prefix="/repositories", tags=["Repositories"])
github_router = APIRouter(prefix="/github", tags=["GitHub App"])


async def _get_or_create_org_id(auth: AuthContext, db: AsyncSession) -> str:
    """Ensure a valid organization ID exists in the database for foreign key constraints."""
    if auth.organization_id:
        return auth.organization_id
    from server.domains.auth.repository import OrganizationRepository

    org_repo = OrganizationRepository(db)
    target_clerk_org_id = auth.clerk_org_id or f"org_{auth.clerk_user_id}"
    org = await org_repo.get_by_clerk_id(target_clerk_org_id)
    if not org:
        org = await org_repo.create(
            clerk_org_id=target_clerk_org_id,
            name="Default Organization",
        )
    return org.id


@router.get("", response_model=list[RepositoryResponse])
async def list_repositories(
    is_active: bool | None = None,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[RepositoryResponse]:
    """List connected repositories for the current organization."""
    org_id = await _get_or_create_org_id(auth, db)
    service = RepositoryService(db)
    repos = await service.list_repositories(org_id, is_active)
    return [RepositoryResponse.model_validate(r) for r in repos]


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> RepositoryResponse:
    """Get single connected repository details."""
    service = RepositoryService(db)
    repo = await service.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return RepositoryResponse.model_validate(repo)


@router.patch("/{repository_id}", response_model=RepositoryResponse)
async def update_repository(
    repository_id: str,
    req: UpdateRepoRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> RepositoryResponse:
    """Update repository active state or settings."""
    service = RepositoryService(db)
    repo = await service.update_repository(
        repository_id=repository_id,
        name=req.name,
        default_branch=req.default_branch,
        is_active=req.is_active,
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return RepositoryResponse.model_validate(repo)


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_repository(
    repository_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Disconnect repository from PullSense."""
    service = RepositoryService(db)
    deleted = await service.disconnect_repository(repository_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )


# ── RepoConfig Endpoints ──────────────────────────────────────────────


@router.get("/{repository_id}/config", response_model=RepoConfigResponse)
async def get_repo_config(
    repository_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> RepoConfigResponse:
    """Get AI review agent configuration for a repository."""
    service = RepositoryService(db)
    config = await service.get_repo_config(repository_id)
    return RepoConfigResponse.model_validate(config)


@router.put("/{repository_id}/config", response_model=RepoConfigResponse)
async def update_repo_config(
    repository_id: str,
    req: UpdateRepoConfigRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> RepoConfigResponse:
    """Update AI review agent toggles and custom rules for a repository."""
    service = RepositoryService(db)
    config = await service.update_repo_config(
        repository_id=repository_id,
        security_agent_enabled=req.security_agent_enabled,
        style_agent_enabled=req.style_agent_enabled,
        test_coverage_agent_enabled=req.test_coverage_agent_enabled,
        auto_review_enabled=req.auto_review_enabled,
        custom_rules=req.custom_rules,
        ignored_paths=req.ignored_paths,
        review_language=req.review_language,
    )
    return RepoConfigResponse.model_validate(config)


# ── GitHub App Repo Sync Endpoints ────────────────────────────────────


@github_router.get("/repositories", response_model=list[GitHubAvailableRepoResponse])
async def list_github_available_repositories(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[GitHubAvailableRepoResponse]:
    """List available repositories from GitHub App installation."""
    org_id = await _get_or_create_org_id(auth, db)
    service = RepositoryService(db)
    return await service.list_available_github_repositories(org_id)


@github_router.post("/repositories/connect", response_model=list[RepositoryResponse])
async def connect_repositories(
    req: ConnectRepositoriesRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[RepositoryResponse]:
    """Connect selected GitHub repositories to organization."""
    org_id = await _get_or_create_org_id(auth, db)
    service = RepositoryService(db)
    available_repos = await service.list_available_github_repositories(org_id)
    repo_map = {r.github_repo_id: r for r in available_repos}

    # Ensure organization has github_installation_id linked
    from server.domains.auth.models import Organization
    org = await db.get(Organization, org_id)
    if org and not org.github_installation_id:
        from server.domains.github.auth import get_app_installations
        installs = await get_app_installations()
        if installs and "id" in installs[0]:
            org.github_installation_id = str(installs[0]["id"])

    connected: list[RepositoryResponse] = []

    for github_repo_id in req.repository_ids:
        r_meta = repo_map.get(github_repo_id)
        full_name = r_meta.full_name if r_meta else f"repo-{github_repo_id}"
        name = r_meta.name if r_meta else f"repo-{github_repo_id}"
        default_branch = r_meta.default_branch if r_meta else "main"
        language = r_meta.language if r_meta else None

        repo = await service.repo.create_or_update(
            organization_id=org_id,
            github_repo_id=github_repo_id,
            full_name=full_name,
            name=name,
            default_branch=default_branch,
            language=language,
            is_active=True,
        )
        connected.append(RepositoryResponse.model_validate(repo))

    await db.commit()
    return connected


@router.post("/{repository_id}/index")
async def trigger_repository_indexing(
    repository_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Trigger Celery background indexing to embed and store repository codebase into Pinecone."""
    service = RepositoryService(db)
    repo = await service.repo.get_by_id(repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    from server.domains.auth.models import Organization

    org = await db.get(Organization, repo.organization_id)
    inst_id = int(org.github_installation_id) if org and org.github_installation_id else None

    if not inst_id:
        raise HTTPException(
            status_code=400,
            detail="No GitHub App installation linked to organization",
        )

    from server.workers.indexing_tasks import index_repository_codebase

    task = index_repository_codebase.delay(repository_id=repo.id, installation_id=inst_id)

    return {"status": "enqueued", "task_id": task.id, "repository_id": repo.id}
