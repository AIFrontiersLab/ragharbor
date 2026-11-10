"""Fallback role: when an upstream stage degraded, restore a safe ordering by prior score."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.stages.base import Stage


class FallbackStage(Stage):
    role = "fallback"

    def process(self, ctx: PipelineContext) -> None:
        if not ctx.degraded:
            ctx.decide(self.name, "noop", reason="healthy")
            return
        for cand in ctx.candidates:
            cand.score = cand.prior_score
        ctx.candidates.sort(key=lambda c: (-c.prior_score, c.doc_id))
        failed = [e.get("stage") for e in ctx.errors]
        ctx.decide(self.name, "restored_prior_order", failed_stages=failed)
