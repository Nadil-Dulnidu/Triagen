"""PullSense Server — Infrastructure: Server-Sent Events (SSE) via Redis Pub/Sub."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any

from server.infrastructure import get_logger
from server.infrastructure.redis import get_redis

logger = get_logger(__name__)


async def publish_review_event(
    review_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """Publish a real-time review progress event to Redis pub/sub channel."""
    channel = f"review:{review_id}"
    event_data = {
        "review_id": review_id,
        "event": event_type,
        "data": payload,
    }
    try:
        redis = get_redis()
        await redis.publish(channel, json.dumps(event_data))
        logger.debug("sse_event_published", channel=channel, event=event_type)
    except Exception as e:
        logger.warning("sse_publish_failed", channel=channel, error=str(e))


async def stream_review_events(
    review_id: str,
    timeout_seconds: int = 300,
) -> AsyncGenerator[str]:
    """Async generator yielding Server-Sent Events for a review channel.

    Subscribes to Redis channel `review:{review_id}` and formats events as:
    `event: <type>\ndata: <json>\n\n`
    """
    channel_name = f"review:{review_id}"
    redis = get_redis()
    pubsub = redis.pubsub()

    await pubsub.subscribe(channel_name)
    logger.info("sse_client_subscribed", channel=channel_name)

    try:
        # Initial connection ping
        init_payload = json.dumps({"review_id": review_id, "status": "listening"})
        yield f"event: connected\ndata: {init_payload}\n\n"

        loop_start = asyncio.get_event_loop().time()
        while True:
            # Check timeout
            if asyncio.get_event_loop().time() - loop_start > timeout_seconds:
                yield f"event: timeout\ndata: {json.dumps({'detail': 'Stream timed out'})}\n\n"
                break

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                raw_data = message["data"]
                try:
                    parsed = json.loads(raw_data)
                    event_type = parsed.get("event", "message")
                    yield f"event: {event_type}\ndata: {json.dumps(parsed.get('data', {}))}\n\n"

                    # If review reaches terminal state, end stream
                    if event_type in {"review.completed", "review.failed"}:
                        break
                except Exception:
                    yield f"data: {raw_data}\n\n"

            await asyncio.sleep(0.1)

    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.aclose()
        logger.info("sse_client_unsubscribed", channel=channel_name)
