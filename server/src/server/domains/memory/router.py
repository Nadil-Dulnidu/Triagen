"""PullSense Server — Memory: REST API Router for Org, Repo, and Developer memory management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.auth.middleware import get_auth_context
from server.domains.auth.schemas import AuthContext
from server.domains.memory.schemas import (
    CreateDeveloperMemoryRequest,
    CreateOrgMemoryRequest,
    CreateRepoMemoryRequest,
    DeveloperMemoryResponse,
    OrgMemoryResponse,
    RepoMemoryResponse,
)
from server.domains.memory.service import MemoryService
from server.infrastructure.database import get_db_session

router = APIRouter(prefix="/memory", tags=["Memory"])


# ── Organization Memory Endpoints ─────────────────────────────────────


@router.get("/org", response_model=list[OrgMemoryResponse])
async def list_org_memories(
    memory_type: str | None = None,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[OrgMemoryResponse]:
    """List organization standards and compliance memories."""
    org_id = auth.organization.id if auth.organization else "00000000-0000-0000-0000-000000000000"
    service = MemoryService(db)
    memories = await service.list_org_memories(org_id, memory_type)
    return [OrgMemoryResponse.model_validate(m) for m in memories]


@router.post(
    "/org",
    response_model=OrgMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_org_memory(
    req: CreateOrgMemoryRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> OrgMemoryResponse:
    """Create a new organization-wide standard or compliance memory."""
    org_id = auth.organization.id if auth.organization else "00000000-0000-0000-0000-000000000000"
    service = MemoryService(db)
    memory = await service.create_org_memory(
        organization_id=org_id,
        memory_type=req.memory_type,
        key=req.key,
        value=req.value,
        metadata=req.metadata,
    )
    return OrgMemoryResponse.model_validate(memory)


@router.delete("/org/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org_memory(
    memory_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete an organization memory rule."""
    service = MemoryService(db)
    deleted = await service.delete_org_memory(memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )


# ── Repository Memory Endpoints ───────────────────────────────────────


@router.get("/repo/{repo_id}", response_model=list[RepoMemoryResponse])
async def list_repo_memories(
    repo_id: str,
    memory_type: str | None = None,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[RepoMemoryResponse]:
    """List architectural conventions and patterns for a repository."""
    service = MemoryService(db)
    memories = await service.list_repo_memories(repo_id, memory_type)
    return [RepoMemoryResponse.model_validate(m) for m in memories]


@router.post(
    "/repo/{repo_id}",
    response_model=RepoMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_repo_memory(
    repo_id: str,
    req: CreateRepoMemoryRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> RepoMemoryResponse:
    """Create a repository convention memory."""
    service = MemoryService(db)
    memory = await service.create_repo_memory(
        repository_id=repo_id,
        memory_type=req.memory_type,
        key=req.key,
        value=req.value,
        metadata=req.metadata,
        relevance_score=req.relevance_score,
    )
    return RepoMemoryResponse.model_validate(memory)


@router.delete("/repo/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repo_memory(
    memory_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a repository memory rule."""
    service = MemoryService(db)
    deleted = await service.delete_repo_memory(memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )


# ── Developer Memory Endpoints ────────────────────────────────────────


@router.get("/developer/{user_id}", response_model=list[DeveloperMemoryResponse])
async def list_developer_memories(
    user_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[DeveloperMemoryResponse]:
    """List developer coding style habits and feedback memories."""
    org_id = auth.organization.id if auth.organization else None
    service = MemoryService(db)
    memories = await service.list_developer_memories(user_id, org_id)
    return [DeveloperMemoryResponse.model_validate(m) for m in memories]


@router.post(
    "/developer/{user_id}",
    response_model=DeveloperMemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_developer_memory(
    user_id: str,
    req: CreateDeveloperMemoryRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> DeveloperMemoryResponse:
    """Create a developer preference memory."""
    org_id = auth.organization.id if auth.organization else "00000000-0000-0000-0000-000000000000"
    service = MemoryService(db)
    memory = await service.create_developer_memory(
        user_id=user_id,
        organization_id=org_id,
        memory_type=req.memory_type,
        key=req.key,
        value=req.value,
        metadata=req.metadata,
        relevance_score=req.relevance_score,
    )
    return DeveloperMemoryResponse.model_validate(memory)


@router.delete("/developer/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_developer_memory(
    memory_id: str,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a developer memory item."""
    service = MemoryService(db)
    deleted = await service.delete_developer_memory(memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )
