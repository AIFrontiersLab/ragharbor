"""Budget role: keep the highest-ranked candidates that fit within the token budget."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.kernel.text import estimate_tokens
from answer_or_abstain_rag.stages.base import Stage


class BudgetStage(Stage):
    role = "budget"

    def process(self, ctx: PipelineContext) -> None:
        budget = self.services.budget_guard.for_request(ctx.request)
        if budget.limit == 0:
            ctx.abstain("budget_exhausted")
            ctx.decide(self.name, "abstain", reason="zero_budget")
            return
        kept = []
        for cand in ctx.candidates:
            cost = estimate_tokens(cand.text or cand.doc_id)
            if not budget.can_afford(cost):
                break
            budget = budget.spend(cost)
            kept.append(cand)
        dropped = len(ctx.candidates) - len(kept)
        ctx.candidates = kept
        ctx.tokens_used = budget.used
        ctx.decide(self.name, "budgeted", limit=budget.limit, used=budget.used, dropped=dropped)
