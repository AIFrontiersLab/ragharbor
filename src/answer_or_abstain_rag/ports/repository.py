"""Persistence port for run records."""

from __future__ import annotations

from typing import Protocol

from answer_or_abstain_rag.application.dto import RunRecord


class RunRepository(Protocol):
    def add(self, record: RunRecord) -> None: ...

    def get(self, run_id: str) -> RunRecord | None: ...

    def list(self, *, limit: int = 50) -> list[RunRecord]: ...

    def remove(self, run_id: str) -> None: ...
