"""Pre- and post-conditions for Ranking Cache.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.ranking_cache.config import RankingCacheConfig
from answer_or_abstain_rag.components.ranking_cache.errors import RankingCacheContractViolation
from answer_or_abstain_rag.components.ranking_cache.models import RankingCacheInput


def validate_input(ctx, config: RankingCacheConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise RankingCacheContractViolation(
            "too many candidates for ranking_cache",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: RankingCacheInput, config: RankingCacheConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise RankingCacheContractViolation("duplicate candidate ids after ranking_cache")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise RankingCacheContractViolation(
                "ranking_cache introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise RankingCacheContractViolation("ranking_cache produced an unsorted ranking")
