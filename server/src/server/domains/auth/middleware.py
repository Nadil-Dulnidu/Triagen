"""PullSense Server — Auth: JWT verification middleware for Clerk tokens."""

from __future__ import annotations

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch JWKS and decode token
    jwks = await _fetch_jwks(settings.clerk_jwks_url)
    claims = _decode_jwt(credentials.credentials, jwks, settings)

    # Extract user identity
    clerk_user_id = claims.get("sub")
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )

    # Extract organization context (if present in session claims)
    clerk_org_id = claims.get("org_id")
    org_role = claims.get("org_role")

    # Look up internal user ID from the database
    # This import is here to avoid circular dependencies
    from server.domains.auth.repository import UserRepository

    # Get DB session from request state (injected by middleware)
    db = request.state.db if hasattr(request.state, "db") else None

    user_id: str | None = None
    organization_id: str | None = None

    if db is not None:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_clerk_id(clerk_user_id)
        if user:
            user_id = user.id

        if clerk_org_id:
            from server.domains.auth.repository import OrganizationRepository

            org_repo = OrganizationRepository(db)
            org = await org_repo.get_by_clerk_id(clerk_org_id)
            if org:
                organization_id = org.id

    return AuthContext(
        user_id=user_id or clerk_user_id,
        clerk_user_id=clerk_user_id,
        organization_id=organization_id,
        clerk_org_id=clerk_org_id,
        org_role=org_role,
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
