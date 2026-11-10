from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.approval import ApprovalStage


def _ctx(classification, run_id="r", options=None):
    return PipelineContext(
        run_id=run_id,
        request=Request.from_dict({"query": "q", "options": options or {}}),
        candidates=[Candidate("a", classification=classification)],
    )


def test_low_risk_auto_approved(services):
    ctx = _ctx("internal")
    ApprovalStage("approval", services).process(ctx)
    assert not ctx.halted


def test_high_risk_requires_approval_then_passes(services):
    ctx = _ctx("restricted", run_id="run-x")
    ApprovalStage("approval", services).process(ctx)
    assert ctx.abstain_reason == "approval_required"
    services.approvals.approve("run-x", "manager")
    again = _ctx("restricted", run_id="run-x")
    ApprovalStage("approval", services).process(again)
    assert not again.halted


def test_approval_token_is_accepted(services):
    token = services.approvals.token_for("run-y")
    ctx = _ctx("restricted", run_id="run-y", options={"approval_token": token})
    ApprovalStage("approval", services).process(ctx)
    assert not ctx.halted
