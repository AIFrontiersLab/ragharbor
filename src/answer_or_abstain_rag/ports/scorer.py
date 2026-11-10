"""Relevance scoring port. Implementations must return values in [0, 1]."""

from __future__ import annotations

from typing import Protocol

from answer_or_abstain_rag.domain.models import Candidate


class RelevanceScorer(Protocol):
    name: str

    def score(self, query: str, candidate: Candidate) -> float: ...
