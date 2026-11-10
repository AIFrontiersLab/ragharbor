"""Named domain events emitted during a run."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.events import DomainEvent

RUN_STARTED = "run.started"
RUN_COMPLETED = "run.completed"
RUN_ABSTAINED = "run.abstained"
RUN_FAILED = "run.failed"
STAGE_COMPLETED = "stage.completed"
STAGE_DEGRADED = "stage.degraded"
CANDIDATE_DENIED = "candidate.denied"
APPROVAL_REQUESTED = "approval.requested"

ALL_EVENTS = (
    RUN_STARTED,
    RUN_COMPLETED,
    RUN_ABSTAINED,
    RUN_FAILED,
    STAGE_COMPLETED,
    STAGE_DEGRADED,
    CANDIDATE_DENIED,
    APPROVAL_REQUESTED,
)


def event(name: str, run_id: str, at: str = "", **payload) -> DomainEvent:
    if name not in ALL_EVENTS:
        raise ValueError(f"unknown event name: {name}")
    return DomainEvent(name=name, run_id=run_id, payload=payload, at=at)
