"""Pre- and post-conditions for Token Budget Governor.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.token_budget_governor.config import TokenBudgetGovernorConfig
from answer_or_abstain_rag.components.token_budget_governor.errors import TokenBudgetGovernorContractViolation
from answer_or_abstain_rag.components.token_budget_governor.models import TokenBudgetGovernorInput


def validate_input(ctx, config: TokenBudgetGovernorConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise TokenBudgetGovernorContractViolation(
            "too many candidates for token_budget_governor",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: TokenBudgetGovernorInput, config: TokenBudgetGovernorConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise TokenBudgetGovernorContractViolation("duplicate candidate ids after token_budget_governor")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise TokenBudgetGovernorContractViolation(
                "token_budget_governor introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise TokenBudgetGovernorContractViolation("token_budget_governor produced an unsorted ranking")
