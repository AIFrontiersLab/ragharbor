"""Bounded retry with exponential backoff. Only retryable errors are retried."""

from __future__ import annotations

from typing import Callable, TypeVar

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock
from answer_or_abstain_rag.kernel.errors import StageError

T = TypeVar("T")


class RetryPolicy:
    def __init__(
        self,
        *,
        attempts: int = 2,
        base_delay: float = 0.05,
        max_delay: float = 1.0,
        clock: Clock | None = None,
    ) -> None:
        self.attempts = max(0, attempts)
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.clock = clock or SystemClock()

    def delays(self) -> list[float]:
        return [min(self.max_delay, self.base_delay * (2**i)) for i in range(self.attempts)]

    def call(self, fn: Callable[[], T], *, is_retryable: Callable[[Exception], bool] | None = None) -> T:
        check = is_retryable or _default_retryable
        schedule = self.delays()
        attempt = 0
        while True:
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 - classification below
                if attempt >= len(schedule) or not check(exc):
                    raise
                self.clock.sleep(schedule[attempt])
                attempt += 1


def _default_retryable(exc: Exception) -> bool:
    return isinstance(exc, StageError) and exc.retryable
