"""Cache role: reuse a previous ranking for an identical (tenant, principal, query, candidates) key."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.kernel.ids import stable_hash
from answer_or_abstain_rag.stages.base import Stage


def cache_key(ctx: PipelineContext) -> str:
    req = ctx.request
    return stable_hash(
        {
            "tenant": req.tenant,
            "roles": sorted(req.principal.roles),
            "groups": sorted(req.principal.groups),
            "query": req.query.lower(),
            "docs": sorted(c.doc_id for c in ctx.candidates),
        }
    )


class CacheStage(Stage):
    role = "cache"

    def process(self, ctx: PipelineContext) -> None:
        if not self.services.settings.cache.enabled or self.services.cache is None:
            ctx.decide(self.name, "skipped", reason="cache_disabled")
            return
        if not ctx.candidates:
            ctx.decide(self.name, "skipped", reason="no_candidates")
            return
        key = cache_key(ctx)
        ctx.metadata["cache_key"] = key
        cached = self.services.cache.get(key)
        if cached is None:
            ctx.decide(self.name, "miss")
            return
        by_id = {c.doc_id: c for c in ctx.candidates}
        ranked = []
        for doc_id, score in cached:
            cand = by_id.get(doc_id)
            if cand is not None:
                cand.score = score
                ranked.append(cand)
        ctx.candidates = ranked
        ctx.cache_hit = True
        ctx.decide(self.name, "hit", count=len(ranked))
