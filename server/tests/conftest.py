"""Test configuration and shared fixtures for pytest."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment variables before importing server modules
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/pullsense_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
os.environ["CLERK_SECRET_KEY"] = "sk_test_mock"
os.environ["CLERK_WEBHOOK_SECRET"] = "whsec_mock"
os.environ["CLERK_JWKS_URL"] = "https://mock.clerk.accounts.dev/.well-known/jwks.json"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["GCP_REGION"] = "us-central1"

from server.main import create_app


@pytest.fixture
def app():
    """Create FastAPI application instance for testing."""
    return create_app()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient]:
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
