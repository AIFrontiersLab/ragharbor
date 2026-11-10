"""Pre- and post-conditions for Relevance Scorer.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.relevance_scorer.config import RelevanceScorerConfig
from answer_or_abstain_rag.components.relevance_scorer.errors import RelevanceScorerContractViolation
from answer_or_abstain_rag.components.relevance_scorer.models import RelevanceScorerInput


def validate_input(ctx, config: RelevanceScorerConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise RelevanceScorerContractViolation(
            "too many candidates for relevance_scorer",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: RelevanceScorerInput, config: RelevanceScorerConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise RelevanceScorerContractViolation("duplicate candidate ids after relevance_scorer")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise RelevanceScorerContractViolation(
                "relevance_scorer introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise RelevanceScorerContractViolation("relevance_scorer produced an unsorted ranking")
