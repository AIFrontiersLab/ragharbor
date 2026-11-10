"""Three-state circuit breaker (closed -> open -> half-open) with an injectable clock."""

from __future__ import annotations

from enum import Enum
from typing import Callable, TypeVar

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock
from answer_or_abstain_rag.kernel.errors import CircuitOpenError

T = TypeVar("T")


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 3,
        reset_seconds: float = 30.0,
        clock: Clock | None = None,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self.clock = clock or SystemClock()
        self._state = BreakerState.CLOSED
        self._failures = 0
        self._opened_at = 0.0

    @property
    def state(self) -> BreakerState:
        if self._state is BreakerState.OPEN and self.clock.monotonic() - self._opened_at >= self.reset_seconds:
            self._state = BreakerState.HALF_OPEN
        return self._state

    @property
    def failures(self) -> int:
        return self._failures

    def call(self, fn: Callable[[], T]) -> T:
        if self.state is BreakerState.OPEN:
            raise CircuitOpenError(self.name)
        try:
            result = fn()
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result

    def _on_success(self) -> None:
        self._failures = 0
        self._state = BreakerState.CLOSED

    def _on_failure(self) -> None:
        self._failures += 1
        if self._state is BreakerState.HALF_OPEN or self._failures >= self.failure_threshold:
            self._state = BreakerState.OPEN
            self._opened_at = self.clock.monotonic()

    def snapshot(self) -> dict:
        return {"name": self.name, "state": self.state.value, "failures": self._failures}
