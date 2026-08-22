"""PullSense Server — Infrastructure: Redis client setup."""

from __future__ import annotations

from typing import Any

import redis.asyncio as aioredis

from server.config import get_settings

_redis_client: aioredis.Redis | None = None


async def init_redis(redis_url: str | None = None) -> aioredis.Redis:
    """Initialize the Redis client.

    Called once during application startup.
    """
    global _redis_client
    settings = get_settings()
    url = redis_url or settings.redis_url
    _redis_client = aioredis.from_url(
        url,
        decode_responses=True,
        max_connections=20,
    )
    # Verify connectivity
    await _redis_client.ping()
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection.

    Called during application shutdown.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> aioredis.Redis:
    """Get the Redis client instance (lazily initialized if needed).

    Usage as FastAPI dependency or background worker helper:
        @router.get("/cached")
        async def get_cached(redis: Redis = Depends(get_redis)):
            ...
    """
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _redis_client


async def publish_event(channel: str, data: dict[str, Any]) -> None:
    """Publish an event to a Redis pub/sub channel.

    Used for SSE real-time updates during review processing.
    """
    import json

    client = get_redis()
    await client.publish(channel, json.dumps(data))
