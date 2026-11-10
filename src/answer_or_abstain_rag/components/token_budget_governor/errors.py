"""Errors raised by Token Budget Governor. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class TokenBudgetGovernorError(StageError):
    code = "token_budget_governor_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("token_budget_governor", message, retryable=retryable, details=details)


class TokenBudgetGovernorContractViolation(TokenBudgetGovernorError):
    code = "token_budget_governor_contract_violation"
