"""PullSense Server — Entry point."""

from __future__ import annotations


def main() -> None:
    """Start the FastAPI application with uvicorn."""
    import uvicorn

    from server.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "server.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.app_log_level.lower(),
    )


if __name__ == "__main__":
    main()
