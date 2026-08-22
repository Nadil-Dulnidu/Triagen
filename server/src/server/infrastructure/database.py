"""PullSense Server — Infrastructure: SQLAlchemy async database engine and session."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from starlette.requests import Request

from server.config import get_settings

# Naming convention for Alembic auto-generated constraints
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides:
    - UUID primary key by default
    - Consistent naming conventions for constraints
    - Type annotation support
    - Eager defaults loading for server-generated columns (timestamps, IDs)
    """

    __mapper_args__ = {"eager_defaults": True}

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )


def import_all_models() -> None:
    """Import all domain models to ensure SQLAlchemy's mapper registry is fully populated."""
    try:
        import server.domains.analytics.models
        import server.domains.auth.models
        import server.domains.memory.models
        import server.domains.repositories.models
        import server.domains.reviews.models
        import server.domains.webhooks.models  # noqa: F401
    except ImportError:
        pass


def create_engine(database_url: str | None = None, **kwargs: Any) -> Any:
    """Create an async SQLAlchemy engine."""
    import_all_models()
    settings = get_settings()
    url = database_url or settings.database_url

    return create_async_engine(
        url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
        echo=settings.app_debug,
        **kwargs,
    )


def create_session_factory(engine: Any) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# Module-level engine and session factory (initialized at app startup)
_engine: Any = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str | None = None) -> None:
    """Initialize the database engine and session factory.

    Called once during application startup.
    """
    global _engine, _session_factory
    _engine = create_engine(database_url)
    _session_factory = create_session_factory(_engine)


async def close_db() -> None:
    """Close the database engine.

    Called during application shutdown.
    """
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


async def run_migrations(database_url: str | None = None) -> None:
    """Apply Alembic migrations to database, or create tables if running in fallback mode."""
    import asyncio
    from pathlib import Path

    import_all_models()
    settings = get_settings()
    url = database_url or settings.database_url

    def _apply_alembic() -> bool:
        try:
            from alembic import command
            from alembic.config import Config

            # Locate alembic.ini
            candidate_paths = [
                Path("/app/migrations/alembic.ini"),
                Path(__file__).resolve().parent.parent.parent.parent / "migrations" / "alembic.ini",
                Path("migrations/alembic.ini"),
                Path("server/migrations/alembic.ini"),
            ]
            ini_path = next((p for p in candidate_paths if p.exists()), None)
            if not ini_path:
                return False

            alembic_cfg = Config(str(ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", url)
            alembic_cfg.set_main_option("script_location", str(ini_path.parent))
            command.upgrade(alembic_cfg, "head")
            return True
        except Exception:
            return False

    migrated = await asyncio.to_thread(_apply_alembic)

    # Fallback: if alembic config wasn't found or failed, ensure tables exist via metadata
    if not migrated:
        global _engine
        if _engine is not None:
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that provides a database session.

    Reuses the request-scoped session from request.state.db if available,
    otherwise creates a new session from the session factory.
    """
    if hasattr(request.state, "db") and request.state.db is not None:
        yield request.state.db
        return

    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
