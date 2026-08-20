"""Alembic environment configuration for async PostgreSQL migrations."""

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Add the server source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import all models so Alembic can detect them
from server.domains.analytics.models import UsageEvent  # noqa: F401
from server.domains.auth.models import Organization, OrganizationMembership, User  # noqa: F401
from server.domains.memory.models import DeveloperMemory, OrgMemory, RepoMemory  # noqa: F401
from server.domains.repositories.models import RepoConfig, RepoMember, Repository  # noqa: F401
from server.domains.reviews.models import (  # noqa: F401
    PullRequest,
    Review,
    ReviewAgentRun,
    ReviewFinding,
)
from server.domains.webhooks.models import WebhookEvent  # noqa: F401
from server.infrastructure.database import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for auto-generation
target_metadata = Base.metadata

# Override sqlalchemy.url from environment if available
database_url = os.getenv(
    "DATABASE_URL",
    config.get_main_option("sqlalchemy.url"),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL without connecting."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations against a live connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
