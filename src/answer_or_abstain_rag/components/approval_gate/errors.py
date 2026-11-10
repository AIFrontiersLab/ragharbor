"""Errors raised by Approval Gate. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class ApprovalGateError(StageError):
    code = "approval_gate_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("approval_gate", message, retryable=retryable, details=details)


class ApprovalGateContractViolation(ApprovalGateError):
    code = "approval_gate_contract_violation"
