"""Answer role: assemble a citation-backed answer, or abstain when evidence is insufficient."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import Answer, Citation, PipelineContext
from answer_or_abstain_rag.kernel.text import snippet
from answer_or_abstain_rag.stages.base import Stage


class AnswerStage(Stage):
    role = "answer"
    critical = True

    def process(self, ctx: PipelineContext) -> None:
        settings = self.services.settings.pipeline
        top_k = ctx.request.top_k or settings.top_k
        eligible = [c for c in ctx.candidates if c.score >= settings.min_score]
        chosen = sorted(eligible, key=lambda c: (-c.score, c.doc_id))[:top_k]
        if not chosen:
            if ctx.request.require_evidence and settings.require_evidence:
                ctx.abstain("insufficient_evidence")
                ctx.decide(self.name, "abstain", reason="insufficient_evidence")
                return
            ctx.answer = Answer(text=f"No supporting evidence found for: {ctx.request.query}. Answer is unverified.")
            ctx.decide(self.name, "answered_unverified")
            return
        citations = [Citation(doc_id=c.doc_id, score=c.score, snippet=snippet(c.text)) for c in chosen]
        refs = ", ".join(f"[{c.doc_id}]" for c in citations)
        text = f"Answer to '{ctx.request.query}' grounded in {len(citations)} source(s): {refs}."
        ctx.answer = Answer(text=text, citations=citations)
        ctx.decide(self.name, "answered", citations=len(citations))
