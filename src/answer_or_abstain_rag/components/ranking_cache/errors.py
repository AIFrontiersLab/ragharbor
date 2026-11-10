"""Errors raised by Ranking Cache. They are ``StageError`` subclasses so the
orchestrator applies its standard retry, breaker, and fallback semantics."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import StageError


class RankingCacheError(StageError):
    code = "ranking_cache_error"

    def __init__(self, message: str, *, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__("ranking_cache", message, retryable=retryable, details=details)


class RankingCacheContractViolation(RankingCacheError):
    code = "ranking_cache_contract_violation"
