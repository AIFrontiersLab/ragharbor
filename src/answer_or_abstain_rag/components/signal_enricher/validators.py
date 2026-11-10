"""Pre- and post-conditions for Signal Enricher.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.signal_enricher.config import SignalEnricherConfig
from answer_or_abstain_rag.components.signal_enricher.errors import SignalEnricherContractViolation
from answer_or_abstain_rag.components.signal_enricher.models import SignalEnricherInput


def validate_input(ctx, config: SignalEnricherConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise SignalEnricherContractViolation(
            "too many candidates for signal_enricher",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: SignalEnricherInput, config: SignalEnricherConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise SignalEnricherContractViolation("duplicate candidate ids after signal_enricher")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise SignalEnricherContractViolation(
                "signal_enricher introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise SignalEnricherContractViolation("signal_enricher produced an unsorted ranking")
