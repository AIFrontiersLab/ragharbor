"""Retrieve role: pull candidates from the corpus when none were supplied."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.stages.base import Stage


class RetrieveStage(Stage):
    role = "retrieve"

    def process(self, ctx: PipelineContext) -> None:
        if ctx.candidates:
            ctx.decide(self.name, "skipped", reason="candidates_supplied")
            return
        if ctx.request.options.get("force_empty_evidence"):
            ctx.decide(self.name, "skipped", reason="force_empty_evidence")
            return
        corpus = self.services.corpus
        if corpus is None or len(corpus) == 0:
            ctx.decide(self.name, "skipped", reason="empty_corpus")
            return
        limit = self.services.settings.pipeline.max_candidates
        ctx.candidates = corpus.search(ctx.request.query, tenant=ctx.request.tenant, limit=limit)
        ctx.decide(self.name, "retrieved", count=len(ctx.candidates))
