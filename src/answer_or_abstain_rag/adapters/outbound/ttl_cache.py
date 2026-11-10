"""Bounded LRU cache with per-entry time-to-live."""

from __future__ import annotations

import threading
from collections import OrderedDict

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock


class TTLRankingCache:
    def __init__(self, capacity: int = 1024, ttl_seconds: float = 300.0, *, clock: Clock | None = None) -> None:
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.clock = clock or SystemClock()
        self._data: "OrderedDict[str, tuple[float, list]]" = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                self.misses += 1
                return None
            stored_at, value = entry
            if self.clock.monotonic() - stored_at > self.ttl:
                del self._data[key]
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return list(value)

    def put(self, key: str, ranking: list) -> None:
        with self._lock:
            self._data[key] = (self.clock.monotonic(), list(ranking))
            self._data.move_to_end(key)
            while len(self._data) > self.capacity:
                self._data.popitem(last=False)

    def invalidate(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._data.clear()
            else:
                self._data.pop(key, None)

    def __len__(self) -> int:
        return len(self._data)
