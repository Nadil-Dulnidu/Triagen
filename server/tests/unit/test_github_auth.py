"""Unit tests for GitHub App authentication and JWT generation."""

from __future__ import annotations

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from server.config import Settings
from server.domains.github.auth import generate_app_jwt


def _generate_test_rsa_key() -> str:
    """Generate a temporary RSA private key for testing."""
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode("utf-8")


def test_generate_app_jwt() -> None:
    """Test generating a valid RS256 JWT for GitHub App."""
    private_key = _generate_test_rsa_key()
    settings = Settings(
        github_app_id=123456,
        github_app_private_key=private_key,
        clerk_secret_key="sk_test",
        clerk_webhook_secret="whsec_test",
        clerk_jwks_url="https://test.clerk.dev",
        gcp_project_id="test-project",
    )

    token = generate_app_jwt(settings)
    assert token is not None

    # Decode unverified to inspect claims
    claims = jwt.decode(token, options={"verify_signature": False})
    assert claims["iss"] == "123456"
    assert "exp" in claims
    assert "iat" in claims
    assert claims["exp"] > claims["iat"]
