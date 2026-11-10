"""Pre- and post-conditions for Approval Gate.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.approval_gate.config import ApprovalGateConfig
from answer_or_abstain_rag.components.approval_gate.errors import ApprovalGateContractViolation
from answer_or_abstain_rag.components.approval_gate.models import ApprovalGateInput


def validate_input(ctx, config: ApprovalGateConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise ApprovalGateContractViolation(
            "too many candidates for approval_gate",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: ApprovalGateInput, config: ApprovalGateConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise ApprovalGateContractViolation("duplicate candidate ids after approval_gate")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise ApprovalGateContractViolation(
                "approval_gate introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise ApprovalGateContractViolation("approval_gate produced an unsorted ranking")
