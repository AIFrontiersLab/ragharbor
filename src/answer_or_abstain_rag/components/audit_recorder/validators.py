"""Pre- and post-conditions for Audit Recorder.

Violations are defects, not transient faults, so they are raised as
non-retryable errors and surface as a degraded (or failed, if critical) stage.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.audit_recorder.config import AuditRecorderConfig
from answer_or_abstain_rag.components.audit_recorder.errors import AuditRecorderContractViolation
from answer_or_abstain_rag.components.audit_recorder.models import AuditRecorderInput


def validate_input(ctx, config: AuditRecorderConfig) -> None:
    if len(ctx.candidates) > config.max_input_candidates:
        raise AuditRecorderContractViolation(
            "too many candidates for audit_recorder",
            details={"limit": config.max_input_candidates, "received": len(ctx.candidates)},
        )


def validate_output(ctx, before: AuditRecorderInput, config: AuditRecorderConfig) -> None:
    ids = [c.doc_id for c in ctx.candidates]
    if len(ids) != len(set(ids)):
        raise AuditRecorderContractViolation("duplicate candidate ids after audit_recorder")
    if not config.may_introduce_ids:
        unexpected = set(ids) - set(before.candidate_ids)
        if unexpected:
            raise AuditRecorderContractViolation(
                "audit_recorder introduced unknown candidates", details={"ids": sorted(unexpected)}
            )
    if config.enforce_sorted_output and not ctx.cache_hit:
        scores = [c.score for c in ctx.candidates]
        if scores != sorted(scores, reverse=True):
            raise AuditRecorderContractViolation("audit_recorder produced an unsorted ranking")
