"""Relevance Scorer.

Scores query-candidate relevance with a deterministic BM25-style reference model.
"""

from answer_or_abstain_rag.components.relevance_scorer.adapter import ROLE, build
from answer_or_abstain_rag.components.relevance_scorer.config import CONFIG, RelevanceScorerConfig
from answer_or_abstain_rag.components.relevance_scorer.errors import RelevanceScorerError
from answer_or_abstain_rag.components.relevance_scorer.service import RelevanceScorerService

__all__ = ["CONFIG", "ROLE", "build", "RelevanceScorerConfig", "RelevanceScorerError", "RelevanceScorerService"]
