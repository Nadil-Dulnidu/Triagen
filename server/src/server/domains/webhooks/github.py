"""PullSense Server — Webhooks: GitHub signature verification."""

from __future__ import annotations

import hashlib
import hmac

from fastapi import HTTPException, Request, status

from server.config import Settings, get_settings
from server.infrastructure import get_logger

logger = get_logger(__name__)


async def verify_github_signature(
    request: Request,
    settings: Settings | None = None,
) -> bytes:
    """Verify GitHub webhook payload signature against the configured webhook secret.

    GitHub passes the signature in the `X-Hub-Signature-256` header formatted as:
    `sha256=<hex_digest>`

    Returns the raw body bytes if valid, or raises HTTPException 401.
    """
    settings = settings or get_settings()
    secret = settings.github_webhook_secret

    if not secret:
        # In development if secret not set, log warning and allow
        if settings.is_development:
            logger.warning("github_webhook_secret_not_configured")
            return await request.body()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub webhook secret is not configured on server.",
        )

    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header.",
        )

    body = await request.body()
    computed_signature = (
        "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(computed_signature, signature_header):
        logger.warning(
            "github_webhook_signature_mismatch",
            received=signature_header,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )

    return body
