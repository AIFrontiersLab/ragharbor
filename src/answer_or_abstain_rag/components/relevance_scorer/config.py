"""Static configuration for the Relevance Scorer component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RelevanceScorerConfig:
    name: str = "relevance_scorer"
    display_name: str = 'Relevance Scorer'
    role: str = "score"
    interface: str = 'score(query, candidate) -> float'
    responsibility: str = 'Scores query-candidate relevance with a deterministic BM25-style reference model.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = True


CONFIG = RelevanceScorerConfig()
