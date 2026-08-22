"""PullSense Server — Auth: JWT verification middleware for Clerk tokens."""

from __future__ import annotations

import contextlib
import json
from typing import Any

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.config import Settings, get_settings
from server.domains.auth.schemas import AuthContext
from server.infrastructure import get_logger

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

# Cache for JWKS keys
_jwks_cache: dict[str, Any] | None = None


async def _fetch_jwks(jwks_url: str) -> dict[str, Any]:
    """Fetch and cache Clerk's JWKS (JSON Web Key Set) for JWT verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def _decode_jwt(token: str, jwks: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Decode and verify a Clerk JWT token using the JWKS public keys."""
    try:
        # Get the signing key from JWKS
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        rsa_key: dict[str, Any] = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = key
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate signing key",
            )

        # Decode with verification
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key))
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # Clerk doesn't set audience by default
                "verify_iss": bool(settings.clerk_issuer),
            },
            issuer=settings.clerk_issuer if settings.clerk_issuer else None,
        )
        return payload

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from e
    except jwt.InvalidTokenError as e:
        logger.warning("jwt_verification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


async def get_auth_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    """FastAPI dependency that extracts and verifies the Clerk JWT.

    Returns an AuthContext with the authenticated user's identity and org context.

    Usage:
        @router.get("/protected")
        async def protected_route(auth: AuthContext = Depends(get_auth_context)):
            print(auth.user_id, auth.organization_id)
    """
    if credentials is None:
        if settings.app_env == "development":
            db = request.state.db if hasattr(request.state, "db") else None
            dev_user_id = "00000000-0000-0000-0000-000000000001"
            dev_org_id = "00000000-0000-0000-0000-000000000001"
            if db is not None:
                from server.domains.auth.repository import OrganizationRepository, UserRepository

                user_repo = UserRepository(db)
                org_repo = OrganizationRepository(db)
                dev_user = await user_repo.get_by_clerk_id("user_dev_local")
                if not dev_user:
                    try:
                        dev_user = await user_repo.create(
                            clerk_user_id="user_dev_local",
                            email="dev@pullsense.local",
                            username="dev_user",
                            display_name="Developer",
                        )
                    except Exception:
                        dev_user = await user_repo.get_by_clerk_id("user_dev_local")
                dev_org = await org_repo.get_by_clerk_id("org_dev_local")
                if not dev_org:
                    try:
                        dev_org = await org_repo.create(
                            clerk_org_id="org_dev_local",
                            name="Default Organization",
                        )
                    except Exception:
                        dev_org = await org_repo.get_by_clerk_id("org_dev_local")
                if dev_org:
                    dev_org_id = dev_org.id
                if dev_user:
                    dev_user_id = dev_user.id
                with contextlib.suppress(Exception):
                    await db.commit()
            return AuthContext(
                user_id=dev_user_id,
                clerk_user_id="user_dev_local",
                organization_id=dev_org_id,
                clerk_org_id="org_dev_local",
                org_role="admin",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch JWKS and decode token
    try:
        jwks = await _fetch_jwks(settings.clerk_jwks_url)
        claims = _decode_jwt(credentials.credentials, jwks, settings)
    except Exception as e:
        if settings.app_env == "development":
            try:
                claims = jwt.decode(
                    credentials.credentials,
                    options={"verify_signature": False},
                )
            except Exception:
                claims = {"sub": "user_dev_local", "org_id": "org_dev_local", "org_role": "admin"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {e}",
            ) from e

    # Extract user identity
    clerk_user_id = claims.get("sub", "user_dev_local")

    # Extract organization context (if present in session claims)
    clerk_org_id = claims.get("org_id")
    org_role = claims.get("org_role")

    # Look up / auto-provision internal user ID and organization from database
    from server.domains.auth.repository import (
        MembershipRepository,
        OrganizationRepository,
        UserRepository,
    )

    # Get DB session from request state (injected by middleware)
    db = request.state.db if hasattr(request.state, "db") else None

    user_id: str | None = None
    organization_id: str | None = None
    target_clerk_org_id = clerk_org_id or f"org_{clerk_user_id}"

    if db is not None:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_clerk_id(clerk_user_id)
        if not user:
            try:
                user = await user_repo.create(
                    clerk_user_id=clerk_user_id,
                    email=claims.get("email") or f"{clerk_user_id}@example.com",
                    username=claims.get("username"),
                    display_name=claims.get("name"),
                )
            except Exception:
                user = await user_repo.get_by_clerk_id(clerk_user_id)

        if user:
            user_id = user.id

        org_repo = OrganizationRepository(db)
        org = await org_repo.get_by_clerk_id(target_clerk_org_id)
        if not org:
            org_name = claims.get("org_name") or (
                f"{user.display_name or user.username or clerk_user_id}'s Workspace"
                if user
                else "Default Organization"
            )
            try:
                org = await org_repo.create(
                    clerk_org_id=target_clerk_org_id,
                    name=org_name,
                )
                if user:
                    mem_repo = MembershipRepository(db)
                    await mem_repo.create(
                        user_id=user.id,
                        organization_id=org.id,
                        role=org_role or "admin",
                    )
            except Exception:
                org = await org_repo.get_by_clerk_id(target_clerk_org_id)

        if org:
            organization_id = org.id

        # Commit newly provisioned records immediately
        with contextlib.suppress(Exception):
            await db.commit()

    return AuthContext(
        user_id=user_id or clerk_user_id,
        clerk_user_id=clerk_user_id,
        organization_id=organization_id,
        clerk_org_id=target_clerk_org_id,
        org_role=org_role or "admin",
    )


async def require_org_admin(
    auth: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    """Dependency that requires the user to be an organization admin."""
    if auth.org_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin role required",
        )
    return auth


async def require_org_member(
    auth: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    """Dependency that requires the user to be at least an organization member."""
    if auth.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required",
        )
    return auth
