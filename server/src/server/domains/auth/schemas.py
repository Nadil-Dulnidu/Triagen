"""PullSense Server — Auth: Pydantic schemas for API requests/responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

# ── Response Schemas ─────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user representation returned by the API."""

    id: str
    email: str
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    github_username: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationResponse(BaseModel):
    """Public organization representation returned by the API."""

    id: str
    name: str
    slug: str | None = None
    github_installation_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberResponse(BaseModel):
    """Organization member with role."""

    id: str
    user: UserResponse
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Auth Context ─────────────────────────────────────────────────────────


class AuthContext(BaseModel):
    """Represents the authenticated user context extracted from JWT.

    Injected into every protected route via FastAPI dependency.
    """

    user_id: str
    clerk_user_id: str
    organization_id: str | None = None
    clerk_org_id: str | None = None
    org_role: str | None = None  # admin | member
