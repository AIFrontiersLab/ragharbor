"""Enrich role: annotate candidates with structural features used downstream and collapse exact duplicates."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.kernel.text import estimate_tokens, tokenize
from answer_or_abstain_rag.stages.base import Stage


class EnrichStage(Stage):
    role = "enrich"

    def process(self, ctx: PipelineContext) -> None:
        query_terms = set(tokenize(ctx.request.query))
        seen_text: dict[str, str] = {}
        kept = []
        collapsed = 0
        for cand in ctx.candidates:
            fingerprint = " ".join(tokenize(cand.text, drop_stopwords=False))
            if fingerprint and fingerprint in seen_text:
                collapsed += 1
                continue
            if fingerprint:
                seen_text[fingerprint] = cand.doc_id
            terms = set(tokenize(cand.text))
            cand.metadata["tokens"] = estimate_tokens(cand.text)
            cand.metadata["query_overlap"] = len(terms & query_terms)
            kept.append(cand)
        ctx.candidates = kept
        ctx.decide(self.name, "enriched", count=len(kept), collapsed=collapsed)
