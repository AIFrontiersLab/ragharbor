"""Policy role: fail-closed access filtering plus PII redaction of surviving text."""

from __future__ import annotations

from answer_or_abstain_rag.domain import events
from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.stages.base import Stage


class PolicyStage(Stage):
    role = "policy"
    critical = True

    def process(self, ctx: PipelineContext) -> None:
        engine = self.services.policy_engine
        principal = ctx.request.principal
        kept = []
        denied = []
        for cand in ctx.candidates:
            decision = engine.evaluate(principal, cand)
            if decision.allowed:
                kept.append(cand)
            else:
                denied.append({"doc_id": cand.doc_id, "reason": decision.reason})
        if self.services.settings.governance.redact_pii:
            redactor = self.services.redactor
            for cand in kept:
                redacted, hits = redactor.redact(cand.text)
                if hits:
                    cand.text = redacted
                    cand.metadata["redactions"] = hits
        ctx.candidates = kept
        ctx.metadata.setdefault("denied", []).extend(denied)
        ctx.decide(self.name, "filtered", kept=len(kept), denied=len(denied))
        if denied:
            ctx.metadata.setdefault("pending_events", []).append(
                (events.CANDIDATE_DENIED, {"count": len(denied)})
            )
