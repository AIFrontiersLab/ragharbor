"""Unit of Work: stage writes and commit them atomically, or roll back."""

from __future__ import annotations

from answer_or_abstain_rag.application.dto import RunRecord


class UnitOfWork:
    def __init__(self, runs) -> None:
        self.runs = runs
        self._staged: list[RunRecord] = []
        self.committed = False

    def __enter__(self) -> "UnitOfWork":
        self._staged = []
        self.committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None or not self.committed:
            self.rollback()

    def add(self, record: RunRecord) -> None:
        self._staged.append(record)

    def commit(self) -> None:
        for record in self._staged:
            self.runs.add(record)
        self._staged = []
        self.committed = True

    def rollback(self) -> None:
        self._staged = []
