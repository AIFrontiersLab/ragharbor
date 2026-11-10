"""Errors raised by Audit Recorder. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class AuditRecorderError(StageError):
    code = "audit_recorder_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("audit_recorder", message, retryable=retryable, details=details)


class AuditRecorderContractViolation(AuditRecorderError):
    code = "audit_recorder_contract_violation"
