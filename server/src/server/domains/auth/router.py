"""PullSense Server — Auth: API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.auth.middleware import get_auth_context
from server.domains.auth.repository import OrganizationRepository, UserRepository
from server.domains.auth.schemas import AuthContext, OrganizationResponse, UserResponse
from server.infrastructure.database import get_db_session

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Get the currently authenticated user's profile."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_clerk_id(auth.clerk_user_id)
    if user is None:
        # Auto-create user on first API call (fallback if webhook hasn't fired yet)
        user = await user_repo.create(
            clerk_user_id=auth.clerk_user_id,
            email=auth.clerk_user_id,  # Will be updated by webhook
        )
    return UserResponse.model_validate(user)


@router.get("/me/organizations", response_model=list[OrganizationResponse])
async def get_user_organizations(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[OrganizationResponse]:
    """List all organizations the current user belongs to."""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)

    user = await user_repo.get_by_clerk_id(auth.clerk_user_id)
    if user is None:
        return []

    orgs = await org_repo.get_user_organizations(user.id)
    return [OrganizationResponse.model_validate(org) for org in orgs]
