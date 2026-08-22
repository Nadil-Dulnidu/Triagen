"""PullSense Server — GitHub: Authentication & installation token generator."""

from __future__ import annotations

import time
from typing import Any

import httpx
import jwt

from server.config import Settings, get_settings
from server.infrastructure import get_logger

logger = get_logger(__name__)

# In-memory cache for installation tokens: {installation_id: (token, expires_at_timestamp)}
_token_cache: dict[int, tuple[str, float]] = {}


def generate_app_jwt(settings: Settings | None = None) -> str:
    """Generate an RS256 JWT signed with the GitHub App's private key.

    GitHub App JWTs are valid for a maximum of 10 minutes.
    Used exclusively to authenticate as the App to request installation tokens.
    """
    settings = settings or get_settings()

    if not settings.github_app_id or not settings.github_app_private_key:
        raise ValueError("GitHub App ID and private key must be configured.")

    # Format the private key if it was stored with escaped newlines in env
    private_key = settings.github_app_private_key
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")

    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60s in the past to account for clock drift
        "exp": now + (9 * 60),  # Expires in 9 minutes
        "iss": str(settings.github_app_id),
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt


async def get_installation_token(
    installation_id: int,
    settings: Settings | None = None,
) -> str:
    """Get an installation access token for a specific GitHub App installation.

    Tokens are cached in memory for up to 50 minutes (GitHub tokens expire in 60 minutes).
    If expired or not in cache, a new token is generated via GitHub API.
    """
    settings = settings or get_settings()
    now = time.time()

    # Check cache
    if installation_id in _token_cache:
        token, expires_at = _token_cache[installation_id]
        if now < expires_at:
            return token

    # Generate new JWT and request installation access token
    app_jwt = generate_app_jwt(settings)
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, headers=headers)
        if not response.is_success:
            logger.error(
                "github_token_exchange_failed",
                installation_id=installation_id,
                status_code=response.status_code,
                response=response.text,
            )
            response.raise_for_status()

        data: dict[str, Any] = response.json()
        token = data["token"]

        # GitHub installation tokens are valid for 1 hour (3600s).
        # Cache for 50 minutes (3000s) for safe margin.
        _token_cache[installation_id] = (token, now + 3000)

        logger.info("github_installation_token_acquired", installation_id=installation_id)
        return token


async def get_app_installations(settings: Settings | None = None) -> list[dict[str, Any]]:
    """List all installations of this GitHub App using the App JWT."""
    settings = settings or get_settings()
    if not settings.github_app_id or not settings.github_app_private_key:
        return []

    try:
        app_jwt = generate_app_jwt(settings)
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        url = "https://api.github.com/app/installations"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.is_success:
                return response.json()
            logger.warning(
                "github_list_installations_failed",
                status_code=response.status_code,
                response=response.text,
            )
    except Exception as e:
        logger.warning("github_get_app_installations_error", error=str(e))
    return []
