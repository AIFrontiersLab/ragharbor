"""Errors raised by Signal Enricher. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class SignalEnricherError(StageError):
    code = "signal_enricher_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("signal_enricher", message, retryable=retryable, details=details)


class SignalEnricherContractViolation(SignalEnricherError):
    code = "signal_enricher_contract_violation"
