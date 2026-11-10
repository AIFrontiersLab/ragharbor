"""Queries: read-only requests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetRun:
    run_id: str


@dataclass(frozen=True)
class ListRuns:
    limit: int = 50


@dataclass(frozen=True)
class DescribePipeline:
    pass
