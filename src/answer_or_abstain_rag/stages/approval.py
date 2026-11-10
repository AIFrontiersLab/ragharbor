"""Approval role: high-risk result sets pause for a human decision before an answer is released."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import PipelineContext
from answer_or_abstain_rag.domain.value_objects import Clearance
from answer_or_abstain_rag.stages.base import Stage


class ApprovalStage(Stage):
    role = "approval"
    critical = True

    def process(self, ctx: PipelineContext) -> None:
        if not ctx.candidates:
            ctx.decide(self.name, "skipped", reason="no_candidates")
            return
        highest = max(Clearance.parse(c.classification) for c in ctx.candidates)
        risk = highest / Clearance.RESTRICTED
        threshold = self.services.settings.governance.approval_risk_threshold
        if risk < threshold:
            ctx.decide(self.name, "auto_approved", risk=round(risk, 3))
            return
        approvals = self.services.approvals
        if approvals.is_approved(ctx.run_id) or ctx.request.options.get("approval_token") == approvals.token_for(ctx.run_id):
            ctx.decide(self.name, "approved", risk=round(risk, 3))
            return
        approvals.request(ctx.run_id, risk=risk, reason=f"classification {highest.label}")
        ctx.decide(self.name, "approval_required", risk=round(risk, 3))
        ctx.abstain("approval_required")
