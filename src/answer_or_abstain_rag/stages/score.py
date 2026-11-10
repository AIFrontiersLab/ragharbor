"""Score role: blend the upstream prior with a query-aware relevance score and reorder."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.stages.base import Stage


class ScoreStage(Stage):
    role = "score"

    def process(self, ctx: PipelineContext) -> None:
        if ctx.cache_hit:
            ctx.decide(self.name, "skipped", reason="cache_hit")
            return
        if not ctx.candidates:
            ctx.decide(self.name, "skipped", reason="no_candidates")
            return
        weight = self.services.settings.pipeline.prior_weight
        top_prior = max((c.prior_score for c in ctx.candidates), default=0.0) or 1.0
        scorer = self.services.scorer
        for cand in ctx.candidates:
            prior = max(0.0, cand.prior_score) / top_prior
            relevance = scorer.score(ctx.request.query, cand) if cand.text else prior
            cand.score = round(weight * prior + (1.0 - weight) * relevance, 6)
            cand.metadata["relevance"] = round(relevance, 6)
        ctx.candidates.sort(key=lambda c: (-c.score, c.doc_id))
        ctx.decide(self.name, "scored", scorer=getattr(scorer, "name", "unknown"), count=len(ctx.candidates))
