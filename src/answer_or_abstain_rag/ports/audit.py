"""Append-only audit sink port."""

from __future__ import annotations

from typing import Protocol


class AuditSink(Protocol):
    def append(self, record: dict) -> None: ...

    def records(self) -> list[dict]: ...
