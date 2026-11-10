"""Ranking cache port. Values are ordered ``(doc_id, score)`` pairs."""

from __future__ import annotations

from typing import Protocol


class RankingCache(Protocol):
    def get(self, key: str) -> list[tuple[str, float]] | None: ...

    def put(self, key: str, ranking: list[tuple[str, float]]) -> None: ...

    def invalidate(self, key: str | None = None) -> None: ...
