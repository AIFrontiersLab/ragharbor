"""Explicit run lifecycle. Illegal transitions raise instead of silently corrupting state."""

from __future__ import annotations

from enum import Enum

from answer_or_abstain_rag.kernel.errors import InvalidTransition


class RunState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    ABSTAINED = "abstained"
    FAILED = "failed"


TRANSITIONS: dict[RunState, frozenset[RunState]] = {
    RunState.PENDING: frozenset({RunState.RUNNING, RunState.FAILED}),
    RunState.RUNNING: frozenset(
        {RunState.COMPLETED, RunState.ABSTAINED, RunState.FAILED, RunState.AWAITING_APPROVAL}
    ),
    RunState.AWAITING_APPROVAL: frozenset({RunState.RUNNING, RunState.FAILED}),
    RunState.COMPLETED: frozenset(),
    RunState.ABSTAINED: frozenset(),
    RunState.FAILED: frozenset(),
}

TERMINAL = frozenset({RunState.COMPLETED, RunState.ABSTAINED, RunState.FAILED})


class RunStateMachine:
    def __init__(self, state: RunState = RunState.PENDING) -> None:
        self.state = state
        self.history: list[RunState] = [state]

    def transition(self, target: RunState) -> None:
        if target not in TRANSITIONS[self.state]:
            raise InvalidTransition(f"cannot move run from {self.state.value} to {target.value}")
        self.state = target
        self.history.append(target)

    @property
    def terminal(self) -> bool:
        return self.state in TERMINAL
