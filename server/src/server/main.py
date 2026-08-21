"""PullSense Server — FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from server.config import get_settings
from server.infrastructure import get_logger, setup_logging
from server.infrastructure.database import close_db, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifecycle manager.

    Initializes infrastructure on startup, cleans up on shutdown.
    """
    settings = get_settings()

    # ── Startup ──────────────────────────────────────────────────────
    setup_logging(
        log_level=settings.app_log_level,
        json_output=settings.is_production,
    )
    logger.info(
        "app_starting",
        env=settings.app_env,
        version=settings.app_version,
    )

    # Initialize database
    init_db(settings.database_url)
    logger.info("database_initialized")

    # Initialize Redis
    try:
        from server.infrastructure.redis import init_redis

        await init_redis(settings.redis_url)
        logger.info("redis_initialized")
    except Exception as e:
        logger.warning("redis_init_failed", error=str(e))

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await close_db()
    logger.info("database_closed")

    try:
        from server.infrastructure.redis import close_redis

        await close_redis()
        logger.info("redis_closed")
    except Exception as e:
        logger.warning("redis_close_failed", error=str(e))

    logger.info("app_stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="AI-Powered GitHub Pull Request Review Platform",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Database session middleware — injects session into request.state
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next: Any) -> Response:
        """Inject a database session into request.state if database is initialized."""
        from server.infrastructure.database import _session_factory

        if _session_factory is not None:
            async with _session_factory() as session:
                request.state.db = session
                return await call_next(request)
        request.state.db = None
        return await call_next(request)

    # ── Routes ───────────────────────────────────────────────────────
    _register_routes(app)

    return app


def _register_routes(app: FastAPI) -> None:
    """Register all API routers."""
    from server.domains.analytics.router import router as analytics_router
    from server.domains.auth.router import router as auth_router
    from server.domains.memory.router import router as memory_router
    from server.domains.repositories.router import (
        github_router,
    )
    from server.domains.repositories.router import (
        router as repositories_router,
    )
    from server.domains.reviews.router import router as reviews_router
    from server.domains.webhooks.router import router as webhook_router

    # Health checks (no prefix)
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {"status": "healthy", "version": get_settings().app_version}

    @app.get("/ready", tags=["Health"])
    async def readiness_check() -> dict[str, str]:
        """Readiness check — verifies database and Redis connectivity."""
        checks: dict[str, str] = {}

        # Check database
        try:
            from server.infrastructure.database import _engine

            if _engine is not None:
                async with _engine.connect() as conn:
                    await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
                checks["database"] = "ok"
            else:
                checks["database"] = "not_initialized"
        except Exception as e:
            checks["database"] = f"error: {e}"

        # Check Redis
        try:
            from server.infrastructure.redis import get_redis

            redis = get_redis()
            await redis.ping()
            checks["redis"] = "ok"
        except Exception as e:
            checks["redis"] = f"error: {e}"

        all_ok = all(v == "ok" for v in checks.values())
        return {"status": "ready" if all_ok else "degraded", **checks}

    # API v1 routes
    api_v1_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_v1_prefix)
    app.include_router(analytics_router, prefix=api_v1_prefix)
    app.include_router(github_router, prefix=api_v1_prefix)
    app.include_router(memory_router, prefix=api_v1_prefix)
    app.include_router(repositories_router, prefix=api_v1_prefix)
    app.include_router(reviews_router, prefix=api_v1_prefix)
    app.include_router(webhook_router, prefix=api_v1_prefix)
