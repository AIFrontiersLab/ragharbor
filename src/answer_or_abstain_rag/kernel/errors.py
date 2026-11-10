"""Error taxonomy.

Every error carries a stable machine-readable ``code`` so adapters (HTTP, CLI,
event consumers) can translate failures without string matching.
"""

from __future__ import annotations


class DomainError(Exception):
    code = "domain_error"
    http_status = 500

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(DomainError):
    code = "validation_error"
    http_status = 400


class PolicyViolation(DomainError):
    code = "policy_violation"
    http_status = 403


class BudgetExceeded(DomainError):
    code = "budget_exceeded"
    http_status = 429


class StageError(DomainError):
    """A stage failed in a way the orchestrator may recover from via fallback."""

    code = "stage_error"
    http_status = 503

    def __init__(self, stage: str, message: str, *, retryable: bool = True, details: dict | None = None) -> None:
        super().__init__(message, details=details)
        self.stage = stage
        self.retryable = retryable


class CircuitOpenError(StageError):
    code = "circuit_open"

    def __init__(self, stage: str) -> None:
        super().__init__(stage, f"circuit for stage '{stage}' is open", retryable=False)


class ConfigurationError(DomainError):
    code = "configuration_error"
    http_status = 500


class NotFound(DomainError):
    code = "not_found"
    http_status = 404


class ApprovalRequired(DomainError):
    code = "approval_required"
    http_status = 202


class InvalidTransition(DomainError):
    code = "invalid_transition"
    http_status = 409
