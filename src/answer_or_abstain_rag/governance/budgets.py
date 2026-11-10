"""Token budget resolution: request budget, bounded by the configured hard limit."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import Request
from answer_or_abstain_rag.domain.value_objects import TokenBudget


class BudgetGuard:
    def __init__(self, default_tokens: int, hard_limit_tokens: int) -> None:
        self.default_tokens = default_tokens
        self.hard_limit_tokens = hard_limit_tokens

    def for_request(self, request: Request) -> TokenBudget:
        requested = self.default_tokens if request.budget_tokens is None else request.budget_tokens
        return TokenBudget(limit=min(requested, self.hard_limit_tokens))
