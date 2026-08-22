"""Test configuration and shared fixtures for pytest."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment variables before importing server modules
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:sql2025#zinD@localhost:5432/pullsense_test"
)
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
os.environ["CLERK_SECRET_KEY"] = "sk_test_mock"
os.environ["CLERK_WEBHOOK_SECRET"] = "whsec_mock"
os.environ["CLERK_JWKS_URL"] = "https://mock.clerk.accounts.dev/.well-known/jwks.json"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["GCP_REGION"] = "us-central1"

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from server.infrastructure.celery_app import celery_app
from server.infrastructure.database import get_db_session
from server.main import create_app

# Enable eager execution for Celery tasks in test environment
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


@pytest.fixture
def mock_db_session():
    """Mock async database session for unit tests."""
    session = AsyncMock()

    def _add(instance):
        if hasattr(instance, "id") and not instance.id:
            instance.id = str(uuid4())

    session.add = MagicMock(side_effect=_add)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=None),
            scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))),
        )
    )
    return session


@pytest.fixture
def app(mock_db_session):
    """Create FastAPI application instance for testing with mocked DB dependency."""
    test_app = create_app()

    async def _override_get_db():
        yield mock_db_session

    test_app.dependency_overrides[get_db_session] = _override_get_db
    return test_app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient]:
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
