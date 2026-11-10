"""Injectable clocks so time-dependent logic (breakers, rate limits, deadlines) is testable."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def monotonic(self) -> float: ...

    def now_iso(self) -> str: ...

    def sleep(self, seconds: float) -> None: ...


class SystemClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


class FakeClock:
    """Manually advanced clock for deterministic tests."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = float(start)
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self._now

    def now_iso(self) -> str:
        return datetime.fromtimestamp(1_700_000_000 + self._now, tz=timezone.utc).isoformat(timespec="milliseconds")

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        self._now += float(seconds)
