"""Unit tests for webhook verification."""

from __future__ import annotations

import hashlib
import hmac
import json
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from server.config import get_settings


def _sign_payload(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.mark.asyncio
async def test_github_webhook_endpoint_accepted(client: AsyncClient) -> None:
    """Test POST /api/v1/webhooks/github accepts valid webhook payload."""
    payload = {
        "action": "opened",
        "number": 1,
        "pull_request": {
            "id": 100,
            "number": 1,
            "title": "Initial feature",
            "state": "open",
            "user": {"id": 1, "login": "testuser"},
            "head": {"ref": "feature", "sha": "1234567890abcdef"},
            "base": {"ref": "main", "sha": "abcdef1234567890"},
        },
        "repository": {
            "id": 200,
            "name": "repo",
            "full_name": "org/repo",
            "owner": {"id": 1, "login": "org"},
        },
        "installation": {"id": 300},
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    secret = get_settings().github_webhook_secret

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": "delivery-123",
        "Content-Type": "application/json",
    }
    if secret:
        headers["X-Hub-Signature-256"] = _sign_payload(secret, body_bytes)

    with patch("server.workers.review_tasks.process_github_pr_review.delay") as mock_delay:
        response = await client.post(
            "/api/v1/webhooks/github",
            content=body_bytes,
            headers=headers,
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "event_id" in data
        mock_delay.assert_called_once()
