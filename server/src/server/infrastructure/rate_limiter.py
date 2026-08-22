"""PullSense Server — Infrastructure: Atomic Redis Token Bucket Rate Limiter."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING

import structlog
from fastapi import HTTPException, Request, Response, status

if TYPE_CHECKING:
    import redis.asyncio as aioredis

logger = structlog.get_logger(__name__)

# Lua script to atomically refill and consume tokens from the bucket
# KEYS[1]: rate_limit_key
# ARGV[1]: max_capacity (number of tokens bucket can hold)
# ARGV[2]: refill_rate (tokens added per second)
# ARGV[3]: current_timestamp (in seconds, float)
# ARGV[4]: requested_tokens (typically 1)
# Returns: {allowed (1 or 0), remaining_tokens, retry_after_seconds}
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_updated')
local tokens = tonumber(data[1])
local last_updated = tonumber(data[2])

if not tokens then
    tokens = capacity
    last_updated = now
else
    local elapsed = math.max(0, now - last_updated)
    tokens = math.min(capacity, tokens + (elapsed * refill_rate))
    last_updated = now
end

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
    return {1, math.floor(tokens), 0}
else
    local needed = requested - tokens
    local retry_after = math.ceil(needed / refill_rate)
    return {0, math.floor(tokens), retry_after}
end
"""  # noqa: S105


class RateLimiter:
    """Production Redis Token Bucket Rate Limiter."""

    def __init__(
        self,
        rate: int = 100,
        per_seconds: int = 3600,
        key_func: Callable[[Request], str] | None = None,
    ) -> None:
        """Initialize RateLimiter.

        Args:
            rate: Maximum number of allowed requests in the time window.
            per_seconds: Duration of the time window in seconds (default: 3600 = 1 hour).
            key_func: Optional custom function to extract the rate limit key from Request.
        """
        self.capacity = rate
        self.refill_rate = rate / per_seconds
        self.per_seconds = per_seconds
        self.key_func = key_func or self._default_key_func
        self._script: aioredis.client.Script | None = None

    @staticmethod
    def _default_key_func(request: Request) -> str:
        """Derive key from organization context, auth header, or client IP."""
        # 1. Check if auth context with organization is present
        auth = getattr(request.state, "auth", None)
        if auth and getattr(auth, "organization_id", None):
            return f"ratelimit:org:{auth.organization_id}"
        if auth and getattr(auth, "user_id", None):
            return f"ratelimit:user:{auth.user_id}"

        # 2. Fallback to client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ratelimit:ip:{ip}"

    async def check(
        self,
        request: Request,
        response: Response | None = None,
        requested_tokens: int = 1,
    ) -> None:
        """Verify request conforms to rate limit.

        Raises HTTPException(429) if exceeded.
        """
        from server.infrastructure.redis import get_redis

        redis_client = await get_redis()
        if redis_client is None:
            # If Redis is temporarily unreachable, fail open to avoid service outage
            return

        key = self.key_func(request)
        now = time.time()

        try:
            res = await redis_client.eval(
                TOKEN_BUCKET_LUA,
                1,
                key,
                str(self.capacity),
                str(self.refill_rate),
                str(now),
                str(requested_tokens),
            )
            allowed, remaining, retry_after = res[0], res[1], res[2]

            if response:
                response.headers["X-RateLimit-Limit"] = str(self.capacity)
                response.headers["X-RateLimit-Remaining"] = str(remaining)

            if allowed == 0:
                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    retry_after=retry_after,
                )
                headers = {
                    "X-RateLimit-Limit": str(self.capacity),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(retry_after),
                }
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Please retry in {retry_after} seconds.",
                    headers=headers,
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("rate_limiter_eval_error", error=str(e))
            # Fail open gracefully on unexpected Redis eval errors


# Default instance: 100 requests / hour per org / client
standard_rate_limiter = RateLimiter(rate=100, per_seconds=3600)
