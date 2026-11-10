"""Per-stage checkpoints so a run's progress is inspectable and resumable."""

from __future__ import annotations

from collections import defaultdict


class CheckpointStore:
    def __init__(self, max_runs: int = 1000) -> None:
        self._data: dict[str, list[dict]] = defaultdict(list)
        self.max_runs = max_runs

    def save(self, run_id: str, stage: str, snapshot: dict) -> None:
        self._data[run_id].append({"stage": stage, **snapshot})
        if len(self._data) > self.max_runs:
            oldest = next(iter(self._data))
            del self._data[oldest]

    def load(self, run_id: str) -> list[dict]:
        return list(self._data.get(run_id, []))

    def last_completed(self, run_id: str) -> str | None:
        entries = self._data.get(run_id) or []
        return entries[-1]["stage"] if entries else None
