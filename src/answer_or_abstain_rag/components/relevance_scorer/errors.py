"""Errors raised by Relevance Scorer. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class RelevanceScorerError(StageError):
    code = "relevance_scorer_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("relevance_scorer", message, retryable=retryable, details=details)


class RelevanceScorerContractViolation(RelevanceScorerError):
    code = "relevance_scorer_contract_violation"
