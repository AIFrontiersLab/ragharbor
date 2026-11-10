"""Append-only JSON Lines run repository. Last write for a run id wins on read."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from answer_or_abstain_rag.application.dto import RunRecord


class JsonlRunRepository:
    def __init__(self, directory: str | Path) -> None:
        self.path = Path(directory) / "runs.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def add(self, record: RunRecord) -> None:
        line = json.dumps({"op": "put", "record": record.to_dict()}, sort_keys=True, default=str)
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def remove(self, run_id: str) -> None:
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"op": "delete", "run_id": run_id}) + "\n")

    def _load(self) -> dict[str, RunRecord]:
        state: dict[str, RunRecord] = {}
        if not self.path.is_file():
            return state
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            entry = json.loads(raw)
            if entry.get("op") == "delete":
                state.pop(entry.get("run_id"), None)
            else:
                record = RunRecord.from_dict(entry["record"])
                state.pop(record.run_id, None)
                state[record.run_id] = record
        return state

    def get(self, run_id: str) -> RunRecord | None:
        return self._load().get(run_id)

    def list(self, *, limit: int = 50) -> list[RunRecord]:
        return list(reversed(self._load().values()))[:limit]
