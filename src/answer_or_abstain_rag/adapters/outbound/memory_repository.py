"""In-memory run repository (default for development and tests)."""

from __future__ import annotations

import threading
from collections import OrderedDict

from answer_or_abstain_rag.application.dto import RunRecord


class InMemoryRunRepository:
    def __init__(self, capacity: int = 10_000) -> None:
        self._items: "OrderedDict[str, RunRecord]" = OrderedDict()
        self._lock = threading.Lock()
        self.capacity = capacity

    def add(self, record: RunRecord) -> None:
        with self._lock:
            self._items[record.run_id] = record
            self._items.move_to_end(record.run_id)
            while len(self._items) > self.capacity:
                self._items.popitem(last=False)

    def get(self, run_id: str) -> RunRecord | None:
        return self._items.get(run_id)

    def list(self, *, limit: int = 50) -> list[RunRecord]:
        return list(reversed(self._items.values()))[:limit]

    def remove(self, run_id: str) -> None:
        with self._lock:
            self._items.pop(run_id, None)

    def __len__(self) -> int:
        return len(self._items)
