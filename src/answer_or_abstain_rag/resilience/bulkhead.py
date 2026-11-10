"""Concurrency bulkhead: reject work beyond a fixed number of in-flight runs."""

from __future__ import annotations

import threading
from contextlib import contextmanager

from answer_or_abstain_rag.kernel.errors import StageError


class Bulkhead:
    def __init__(self, name: str, limit: int) -> None:
        self.name = name
        self.limit = limit
        self._in_flight = 0
        self._lock = threading.Lock()

    @property
    def in_flight(self) -> int:
        return self._in_flight

    @contextmanager
    def slot(self):
        with self._lock:
            if self._in_flight >= self.limit:
                raise StageError(self.name, "bulkhead full", retryable=False, details={"limit": self.limit})
            self._in_flight += 1
        try:
            yield
        finally:
            with self._lock:
                self._in_flight -= 1
