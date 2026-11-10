"""Ingest role: normalise, de-duplicate, and bound the candidate set."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import Candidate, PipelineContext
from answer_or_abstain_rag.kernel.text import normalize
from answer_or_abstain_rag.stages.base import Stage


class IngestStage(Stage):
    role = "ingest"
    critical = True

    def process(self, ctx: PipelineContext) -> None:
        request = ctx.request
        if request.options.get("force_empty_evidence"):
            ctx.candidates = []
            ctx.decide(self.name, "cleared", reason="force_empty_evidence")
            return
        candidates = [self._copy(c) for c in request.candidates]
        if not candidates and request.evidence_ids:
            candidates = [
                Candidate(doc_id=eid, prior_score=1.0, score=1.0, classification="public")
                for eid in request.evidence_ids
            ]
            ctx.decide(self.name, "synthesized_from_evidence_ids", count=len(candidates))
        deduped: dict[str, Candidate] = {}
        for cand in candidates:
            existing = deduped.get(cand.doc_id)
            if existing is None or cand.prior_score > existing.prior_score:
                deduped[cand.doc_id] = cand
        limit = self.services.settings.pipeline.max_candidates
        ordered = sorted(deduped.values(), key=lambda c: (-c.prior_score, c.doc_id))
        if len(ordered) > limit:
            ctx.decide(self.name, "truncated", dropped=len(ordered) - limit)
        ctx.candidates = ordered[:limit]
        ctx.decide(self.name, "ingested", received=len(candidates), kept=len(ctx.candidates))

    @staticmethod
    def _copy(c: Candidate) -> Candidate:
        return Candidate(
            doc_id=c.doc_id,
            text=normalize(c.text),
            prior_score=c.prior_score,
            score=c.prior_score,
            classification=c.classification,
            acl=c.acl,
            metadata=dict(c.metadata),
        )
