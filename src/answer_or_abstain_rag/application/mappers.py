"""Translate between domain objects and DTOs."""

from __future__ import annotations

from answer_or_abstain_rag.application.dto import RunRecord
from answer_or_abstain_rag.domain.models import Outcome


def outcome_to_record(outcome: Outcome, request: dict, *, at: str, checkpoints: list[dict]) -> RunRecord:
    return RunRecord(
        run_id=outcome.run_id,
        status=outcome.status,
        request=dict(request),
        outcome=outcome.to_dict(),
        created_at=at,
        updated_at=at,
        checkpoints=list(checkpoints),
    )


def record_summary(record: RunRecord) -> dict:
    answer = record.outcome.get("answer") or {}
    return {
        "run_id": record.run_id,
        "status": record.status,
        "abstain_reason": record.outcome.get("abstain_reason"),
        "citations": len(answer.get("citations") or []),
        "degraded": record.outcome.get("degraded", False),
        "created_at": record.created_at,
    }
