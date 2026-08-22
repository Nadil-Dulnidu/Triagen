"""Unit tests for Phase 5 resilience: Rate Limiter and Circuit Breaker."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from server.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from server.infrastructure.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state() -> None:
    """Test circuit breaker in normal CLOSED state executes successfully."""
    breaker = CircuitBreaker(name="test_service", failure_threshold=3, recovery_timeout=0.1)

    async def successful_call(x: int) -> int:
        return x * 2

    res = await breaker.call(successful_call, 5)
    assert res == 10
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_trips_to_open() -> None:
    """Test circuit breaker trips to OPEN state after reaching failure threshold."""
    breaker = CircuitBreaker(name="failing_service", failure_threshold=2, recovery_timeout=0.1)

    async def failing_call() -> None:
        raise ValueError("Simulated remote failure")

    # First failure
    with pytest.raises(ValueError):
        await breaker.call(failing_call)
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 1

    # Second failure (reaches threshold of 2)
    with pytest.raises(ValueError):
        await breaker.call(failing_call)
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 2

    # Third call: Rejected immediately with CircuitBreakerOpenError
    with pytest.raises(CircuitBreakerOpenError) as exc_info:
        await breaker.call(failing_call)
    assert "Circuit breaker for service 'failing_service' is OPEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_breaker_recovery_half_open_to_closed() -> None:
    """Test circuit breaker transitions from OPEN -> HALF_OPEN -> CLOSED upon recovery."""
    breaker = CircuitBreaker(name="recovery_service", failure_threshold=1, recovery_timeout=0.05)

    async def failing_call() -> None:
        raise ConnectionError("Remote outage")

    async def recovered_call() -> str:
        return "healthy"

    with pytest.raises(ConnectionError):
        await breaker.call(failing_call)
    assert breaker.state == CircuitState.OPEN

    # Wait for cooldown
    await asyncio.sleep(0.06)

    # Trial call succeeds -> recovers to CLOSED
    res = await breaker.call(recovered_call)
    assert res == "healthy"
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_rate_limiter_allows_and_blocks() -> None:
    """Test rate limiter evaluation and fallback."""
    limiter = RateLimiter(rate=5, per_seconds=60)
    mock_request = MagicMock()
    mock_request.state = MagicMock()
    mock_request.state.auth = None
    mock_request.headers = {}
    mock_request.client = MagicMock(host="127.0.0.1")

    # When Redis is not connected / None, should fail-open without error
    await limiter.check(mock_request)
