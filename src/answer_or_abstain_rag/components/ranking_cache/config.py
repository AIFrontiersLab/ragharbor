"""Static configuration for the Ranking Cache component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RankingCacheConfig:
    name: str = "ranking_cache"
    display_name: str = 'Ranking Cache'
    role: str = "cache"
    interface: str = 'lookup(key) -> ranking | None'
    responsibility: str = 'Short-circuits repeated identical requests with a TTL-bounded ranking cache keyed by principal.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = False


CONFIG = RankingCacheConfig()
