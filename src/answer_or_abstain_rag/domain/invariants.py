"""Post-conditions every outcome must satisfy. Checked in tests and at runtime in strict mode."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import Outcome


def check_outcome(outcome: Outcome, *, require_evidence: bool = True) -> list[str]:
    violations: list[str] = []
    if outcome.answer is not None:
        if require_evidence and not outcome.answer.citations:
            violations.append("answered without evidence while evidence is required")
        scores = [c.score for c in outcome.answer.citations]
        if scores != sorted(scores, reverse=True):
            violations.append("citations are not ordered by descending score")
        ids = outcome.answer.evidence_ids
        if len(ids) != len(set(ids)):
            violations.append("duplicate citations")
    else:
        if not outcome.abstain_reason:
            violations.append("abstained without a reason")
    if not outcome.events:
        violations.append("no stage events recorded")
    return violations
