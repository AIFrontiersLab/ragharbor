"""Cooperative deadlines. Stages check ``remaining()``; the orchestrator flags overruns."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock


class Deadline:
    def __init__(self, budget_ms: float, *, clock: Clock | None = None) -> None:
        self.clock = clock or SystemClock()
        self.budget_ms = float(budget_ms)
        self._start = self.clock.monotonic()

    def elapsed_ms(self) -> float:
        return (self.clock.monotonic() - self._start) * 1000.0

    def remaining_ms(self) -> float:
        return max(0.0, self.budget_ms - self.elapsed_ms())

    def expired(self) -> bool:
        return self.elapsed_ms() > self.budget_ms
