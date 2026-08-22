"""PullSense Server — Infrastructure: Circuit Breaker for Resilient External Integrations."""

from __future__ import annotations

import asyncio
import functools
import inspect
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class CircuitState(StrEnum):
    CLOSED = "CLOSED"      # Normal operation: requests pass through
    OPEN = "OPEN"          # Failing: requests are fast-failed without calling remote service
    HALF_OPEN = "HALF_OPEN"  # Probing: trial request allowed to verify remote recovery


class CircuitBreakerOpenError(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""

    def __init__(self, service_name: str, retry_after: float) -> None:
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker for service '{service_name}' is OPEN. "
            f"Please retry after {retry_after:.1f} seconds."
        )


# Backward-compatibility alias
CircuitBreakerOpenException = CircuitBreakerOpenError


class CircuitBreaker:
    """Circuit Breaker protecting external APIs (GitHub REST, Vertex AI, Pinecone)."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute async function wrapped in the circuit breaker state machine."""
        async with self._lock:
            now = time.time()

            if self.state == CircuitState.OPEN:
                if now - self.last_failure_time >= self.recovery_timeout:
                    logger.info("circuit_breaker_half_open", service=self.name)
                    self.state = CircuitState.HALF_OPEN
                else:
                    retry_after = self.recovery_timeout - (now - self.last_failure_time)
                    logger.warning(
                        "circuit_breaker_rejected",
                        service=self.name,
                        retry_after=retry_after,
                    )
                    raise CircuitBreakerOpenError(self.name, retry_after)

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # On success: reset failures if state was half-open or closed
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    logger.info("circuit_breaker_closed", service=self.name)
                    self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result
        except self.expected_exceptions as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                logger.error(
                    "circuit_breaker_failure",
                    service=self.name,
                    error=str(e),
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold,
                )

                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.critical(
                        "circuit_breaker_opened",
                        service=self.name,
                        cooldown=self.recovery_timeout,
                    )

            raise e


# Registry of global circuit breakers
_BREAKERS: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
) -> CircuitBreaker:
    """Get or create a named CircuitBreaker singleton."""
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    return _BREAKERS[name]


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
) -> Callable[[F], F]:
    """Decorator to wrap an async function in a named circuit breaker."""
    breaker = get_circuit_breaker(name, failure_threshold, recovery_timeout)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
